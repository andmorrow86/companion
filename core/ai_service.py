"""
AI Service module for integrating with OpenAI and Grok for enhanced conversation capabilities
"""
import os
from typing import Optional, Dict, List
from abc import ABC, abstractmethod
import json


class AIServiceBase(ABC):
    """Abstract base class for AI services"""
    
    def __init__(self, api_key: str, model: str, temperature: float = 0.7):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
    
    @abstractmethod
    def generate_response(self, messages: List[Dict], context: Optional[Dict] = None) -> str:
        """Generate a response based on conversation history and context"""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test if the API connection is working"""
        pass


class OpenAIService(AIServiceBase):
    """OpenAI GPT integration for conversation management"""
    
    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview", temperature: float = 0.7):
        super().__init__(api_key, model, temperature)
        try:
            import openai
            self.client = openai.OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError("OpenAI package not installed. Install with: pip install openai")
    
    def generate_response(self, messages: List[Dict], context: Optional[Dict] = None) -> str:
        """
        Generate response using OpenAI's API
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            context: Additional context about the booking situation
        
        Returns:
            Generated response text
        """
        try:
            # Add system context if available
            if context:
                system_context = self._build_system_context(context)
                if system_context:
                    messages.insert(0, {
                        "role": "system",
                        "content": system_context
                    })
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
            raise Exception(f"Failed to generate response: {str(e)}")
    
    def _build_system_context(self, context: Dict) -> str:
        """Build system context message from booking context"""
        business_name = context.get("business_name", "Massage Therapy")
        services = context.get("services", {})
        booking_stage = context.get("booking_stage", "greeting")
        
        system_prompt = f"""You are a helpful booking assistant for {business_name}. Your role is to assist clients with:

1. Booking massage appointments
2. Providing information about services and pricing
3. Checking availability
4. Rescheduling or cancelling appointments
5. Answering questions about policies

Current conversation stage: {booking_stage}

Available services:
"""
        
        for service_key, service_info in services.items():
            system_prompt += f"- {service_info['name']}: {service_info['duration']} min - ${service_info['price']}\n"
        
        system_prompt += """

Guidelines:
- Be warm, welcoming, and professional
- Ask clarifying questions when needed
- Keep responses concise but informative
- Guide clients through the booking process step by step
- If you cannot help, suggest contacting the business directly
- Never make up information about availability or pricing
- Always be helpful and patient
"""
        
        return system_prompt
    
    def test_connection(self) -> bool:
        """Test OpenAI API connection"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            return True
        except Exception:
            return False


class GrokService(AIServiceBase):
    """Grok (xAI) integration for conversation management"""
    
    def __init__(self, api_key: str, model: str = "grok-1", temperature: float = 0.7):
        super().__init__(api_key, model, temperature)
        try:
            import anthropic
            # Note: Using anthropic client for Grok until official SDK is available
            # This is a placeholder - actual Grok integration may require different client
            self.client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            raise ImportError("Anthropic package not installed. Install with: pip install anthropic")
    
    def generate_response(self, messages: List[Dict], context: Optional[Dict] = None) -> str:
        """
        Generate response using Grok's API
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            context: Additional context about the booking situation
        
        Returns:
            Generated response text
        """
        try:
            # Convert OpenAI-style messages to Anthropic format
            # Note: This is a simplified conversion - actual implementation may need adjustment
            system_message = ""
            user_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                elif msg["role"] == "user":
                    user_messages.append({"role": "user", "content": msg["content"]})
                elif msg["role"] == "assistant":
                    user_messages.append({"role": "assistant", "content": msg["content"]})
            
            # Add system context if available
            if context and not system_message:
                system_message = self._build_system_context(context)
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                system=system_message,
                messages=user_messages,
                temperature=self.temperature
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            print(f"Grok API error: {e}")
            raise Exception(f"Failed to generate response: {str(e)}")
    
    def _build_system_context(self, context: Dict) -> str:
        """Build system context message from booking context"""
        # Similar to OpenAI implementation
        business_name = context.get("business_name", "Massage Therapy")
        services = context.get("services", {})
        booking_stage = context.get("booking_stage", "greeting")
        
        system_prompt = f"""You are a helpful booking assistant for {business_name}. 

Available services:
"""
        
        for service_key, service_info in services.items():
            system_prompt += f"- {service_info['name']}: {service_info['duration']} min - ${service_info['price']}\n"
        
        system_prompt += f"""
Current stage: {booking_stage}
Be helpful, professional, and guide clients through booking.
"""
        
        return system_prompt
    
    def test_connection(self) -> bool:
        """Test Grok API connection"""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hello"}]
            )
            return True
        except Exception:
            return False


class RuleBasedService(AIServiceBase):
    """Rule-based fallback when AI is not available"""
    
    def __init__(self, api_key: str = "", model: str = "", temperature: float = 0.0):
        # Ignored parameters for rule-based service
        pass
    
    def generate_response(self, messages: List[Dict], context: Optional[Dict] = None) -> str:
        """Generate rule-based response"""
        if not messages:
            return "How can I help you with your booking today?"
        
        last_message = messages[-1].get("content", "").lower()
        
        # Simple rule-based responses
        if "book" in last_message or "appointment" in last_message:
            return "I'd be happy to help you book an appointment! What type of massage are you interested in?"
        
        elif "service" in last_message or "offer" in last_message or "menu" in last_message:
            services = context.get("services", {}) if context else {}
            if services:
                service_list = "\n".join([f"• {s['name']}: ${s['price']}" for s in services.values()])
                return f"Here are our services:\n{service_list}\n\nWhich one would you like to book?"
            return "Please tell me which service you're interested in."
        
        elif "price" in last_message or "cost" in last_message:
            return "Our prices vary by service type. Would you like me to tell you about our available services and their prices?"
        
        elif "cancel" in last_message:
            return "I can help you cancel your appointment. Please provide your phone number so I can look up your booking."
        
        elif "reschedule" in last_message or "change" in last_message:
            return "I'd be happy to help you reschedule. Please provide your phone number and your preferred new date and time."
        
        elif "available" in last_message or "open" in last_message or "hours" in last_message:
            return "I can check availability for you. What date would you like to check?"
        
        else:
            return "I'm here to help with booking appointments, checking availability, or answering questions about our services. What would you like to do?"
    
    def test_connection(self) -> bool:
        """Rule-based service always works"""
        return True


class AIServiceFactory:
    """Factory for creating AI service instances"""
    
    @staticmethod
    def create_service(provider: str, config: Dict) -> AIServiceBase:
        """
        Create an AI service instance based on provider
        
        Args:
            provider: "openai", "grok", or "rule_based"
            config: Dictionary with configuration parameters
        
        Returns:
            AI service instance
        """
        provider = provider.lower()
        
        if provider == "openai":
            api_key = config.get("openai_api_key", os.getenv("OPENAI_API_KEY"))
            model = config.get("openai_model", os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"))
            temperature = float(config.get("openai_temperature", os.getenv("OPENAI_TEMPERATURE", "0.7")))
            
            if not api_key:
                raise ValueError("OpenAI API key not configured")
            
            return OpenAIService(api_key, model, temperature)
        
        elif provider == "grok":
            api_key = config.get("grok_api_key", os.getenv("GROK_API_KEY"))
            model = config.get("grok_model", os.getenv("GROK_MODEL", "grok-1"))
            temperature = float(config.get("grok_temperature", os.getenv("GROK_TEMPERATURE", "0.7")))
            
            if not api_key:
                raise ValueError("Grok API key not configured")
            
            return GrokService(api_key, model, temperature)
        
        elif provider == "rule_based":
            return RuleBasedService()
        
        else:
            raise ValueError(f"Unknown AI provider: {provider}")


class AIEnhancedBookingAgent:
    """Enhanced booking agent with AI integration"""
    
    def __init__(self, provider: str = "openai", config: Optional[Dict] = None):
        """
        Initialize AI-enhanced booking agent
        
        Args:
            provider: AI provider to use ("openai", "grok", "rule_based")
            config: Configuration dictionary
        """
        self.config = config or {}
        self.provider = provider
        self.ai_service = AIServiceFactory.create_service(provider, self.config)
        self.conversation_history: Dict[str, List[Dict]] = {}
    
    def generate_response(self, phone_number: str, user_message: str, 
                         context: Dict, use_ai: bool = True) -> str:
        """
        Generate response to user message
        
        Args:
            phone_number: Client's phone number
            user_message: User's message
            context: Booking context (services, stage, etc.)
            use_ai: Whether to use AI or fall back to rule-based
        
        Returns:
            Generated response
        """
        try:
            # Get or create conversation history
            if phone_number not in self.conversation_history:
                self.conversation_history[phone_number] = []
            
            # Add user message to history
            self.conversation_history[phone_number].append({
                "role": "user",
                "content": user_message
            })
            
            # Generate response
            if use_ai and self.provider != "rule_based":
                response = self.ai_service.generate_response(
                    self.conversation_history[phone_number],
                    context
                )
            else:
                response = self.ai_service.generate_response(
                    [{"role": "user", "content": user_message}],
                    context
                )
            
            # Add assistant response to history
            self.conversation_history[phone_number].append({
                "role": "assistant",
                "content": response
            })
            
            # Keep history manageable (last 10 messages)
            if len(self.conversation_history[phone_number]) > 10:
                self.conversation_history[phone_number] = self.conversation_history[phone_number][-10:]
            
            return response
            
        except Exception as e:
            print(f"Error generating AI response: {e}")
            # Fall back to rule-based on error
            if use_ai:
                print("Falling back to rule-based response")
                return self.generate_response(phone_number, user_message, context, use_ai=False)
            return "I'm having trouble processing your request. Please try again or contact us directly."
    
    def clear_history(self, phone_number: str):
        """Clear conversation history for a phone number"""
        if phone_number in self.conversation_history:
            del self.conversation_history[phone_number]
    
    def test_ai_connection(self) -> bool:
        """Test if AI service is connected and working"""
        return self.ai_service.test_connection()