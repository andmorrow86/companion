"""
AI-Enhanced Booking Agent that integrates OpenAI/Grok for natural conversations
"""
import os
import sys
from typing import Dict, Optional, List
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.client import ClientManager
from models.appointment import AppointmentManager
from core.scheduler import Scheduler
from core.payment_processor import PaymentProcessor
from core.nlu import NLU
from core.ai_service import AIEnhancedBookingAgent
from config.settings import (
    DATA_DIR, LOGS_DIR, BOOKING_CONFIRMATION, WELCOME_MESSAGE,
    DEPOSIT_ENABLED, BUSINESS_NAME, SERVICES
)


class AIBookingAgent:
    """
    Enhanced booking agent with AI-powered conversation capabilities
    Combines structured booking logic with AI-generated responses
    """
    
    def __init__(self, ai_provider: str = "openai"):
        """
        Initialize AI booking agent
        
        Args:
            ai_provider: AI provider to use ("openai", "grok", "rule_based")
        """
        # Initialize core managers
        self.client_manager = ClientManager(DATA_DIR)
        self.appointment_manager = AppointmentManager(DATA_DIR)
        self.scheduler = Scheduler(self.appointment_manager)
        self.payment_processor = PaymentProcessor()
        self.nlu = NLU()
        
        # Initialize AI service
        ai_config = {
            "openai_api_key": os.getenv("OPENAI_API_KEY"),
            "openai_model": os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"),
            "openai_temperature": float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
            "grok_api_key": os.getenv("GROK_API_KEY"),
            "grok_model": os.getenv("GROK_MODEL", "grok-1"),
            "grok_temperature": float(os.getenv("GROK_TEMPERATURE", "0.7"))
        }
        
        try:
            self.ai_agent = AIEnhancedBookingAgent(ai_provider, ai_config)
            self.ai_enabled = True
            print(f"✓ AI service initialized with {ai_provider}")
        except Exception as e:
            print(f"⚠ AI service not available: {e}")
            print("ℹ Falling back to rule-based responses")
            self.ai_agent = AIEnhancedBookingAgent("rule_based", {})
            self.ai_enabled = False
        
        # Conversation state management
        self.conversations: Dict[str, Dict] = {}
        
        # Ensure directories exist
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create necessary directories"""
        for directory in [DATA_DIR, LOGS_DIR]:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    def _get_conversation_state(self, phone_number: str) -> Dict:
        """Get or create conversation state for a client"""
        phone_number = phone_number.strip().replace("-", "").replace(" ", "")
        
        if phone_number not in self.conversations:
            self.conversations[phone_number] = {
                "stage": "greeting",
                "service": None,
                "date": None,
                "time": None,
                "appointment_id": None,
                "payment_intent_id": None,
                "client": self.client_manager.get_or_create_client(phone_number),
                "messages": [],
                "use_structured_flow": True  # Toggle between AI and structured flow
            }
        
        return self.conversations[phone_number]
    
    def _build_ai_context(self, state: Dict) -> Dict:
        """Build context for AI response generation"""
        return {
            "business_name": BUSINESS_NAME,
            "services": SERVICES,
            "booking_stage": state["stage"],
            "selected_service": state.get("service"),
            "selected_date": state.get("date"),
            "selected_time": state.get("time"),
            "client_name": state["client"].name if state["client"].name else "Valued Client",
            "deposit_enabled": DEPOSIT_ENABLED
        }
    
    def _should_use_structured_flow(self, state: Dict, message: str) -> bool:
        """
        Determine if we should use structured booking flow or AI conversation
        
        Returns True for structured flow, False for AI conversation
        """
        # Use structured flow for booking actions
        booking_keywords = ["book", "schedule", "appointment", "reserve", "tomorrow", "monday", 
                          "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
                          "cancel", "reschedule"]
        
        message_lower = message.lower()
        
        # Check if message contains booking-related keywords
        for keyword in booking_keywords:
            if keyword in message_lower:
                return True
        
        # Check if we're in middle of booking process
        if state["stage"] not in ["greeting", "confirmed"]:
            return True
        
        # Use AI for general inquiries and conversation
        return False
    
    def process_message(self, phone_number: str, message: str) -> str:
        """
        Process incoming message with AI enhancement
        
        Args:
            phone_number: Client's phone number
            message: The message content
        
        Returns:
            Response message
        """
        # Log the message
        self._log_message(phone_number, message, is_client=True)
        
        # Get conversation state
        state = self._get_conversation_state(phone_number)
        
        # Try to parse with NLU first
        intent, extracted_data = self.nlu.parse_booking_request(message)
        
        # Update state with extracted data
        self._update_state_from_extraction(state, extracted_data)
        
        # Decide on response strategy
        use_structured = self._should_use_structured_flow(state, message)
        
        if use_structured or not self.ai_enabled:
            # Use structured booking flow
            response = self._handle_structured_flow(state, intent, extracted_data, message)
        else:
            # Use AI conversation
            response = self._handle_ai_conversation(state, message, intent)
        
        # Log the response
        self._log_message(phone_number, response, is_client=False)
        
        return response
    
    def _update_state_from_extraction(self, state: Dict, extracted_data: Dict):
        """Update conversation state from NLU extraction"""
        if extracted_data.get("service"):
            state["service"] = extracted_data["service"]
        if extracted_data.get("date"):
            state["date"] = extracted_data["date"]
        if extracted_data.get("time"):
            state["time"] = extracted_data["time"]
        if extracted_data.get("name"):
            state["client"].name = extracted_data["name"]
        if extracted_data.get("email"):
            state["client"].email = extracted_data["email"]
    
    def _handle_structured_flow(self, state: Dict, intent: str, 
                               extracted_data: Dict, original_message: str) -> str:
        """Handle message using structured booking logic"""
        stage = state["stage"]
        
        # Import the original booking agent logic
        from agent.booking_agent import BookingAgent
        original_agent = BookingAgent()
        
        # Use the original agent's structured flow
        return original_agent._handle_message(state, intent, extracted_data, original_message)
    
    def _handle_ai_conversation(self, state: Dict, message: str, intent: str) -> str:
        """Handle message using AI conversation"""
        try:
            # Build context for AI
            context = self._build_ai_context(state)
            
            # Generate AI response
            ai_response = self.ai_agent.generate_response(
                state["client"].phone_number,
                message,
                context,
                use_ai=True
            )
            
            # If AI response suggests booking, switch to structured flow
            booking_indicators = ["book", "schedule", "appointment", "reserve"]
            if any(indicator in ai_response.lower() for indicator in booking_indicators):
                state["use_structured_flow"] = True
            
            return ai_response
            
        except Exception as e:
            print(f"AI conversation error: {e}")
            # Fall back to structured flow
            return self._handle_structured_flow(state, intent, {}, message)
    
    def _log_message(self, phone_number: str, message: str, is_client: bool = True):
        """Log messages for debugging and analysis"""
        log_file = os.path.join(LOGS_DIR, f"{phone_number}.log")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(log_file, 'a') as f:
            direction = "CLIENT" if is_client else "AGENT"
            ai_mode = "AI" if is_client else "AI" if self.ai_enabled else "RULE"
            f.write(f"[{timestamp}] {direction} ({ai_mode}): {message}\n")
    
    def reset_conversation(self, phone_number: str):
        """Reset conversation to initial state"""
        phone_number = phone_number.strip().replace("-", "").replace(" ", "")
        
        if phone_number in self.conversations:
            del self.conversations[phone_number]
        
        # Also clear AI conversation history
        if self.ai_enabled:
            self.ai_agent.clear_history(phone_number)
    
    def get_conversation_info(self, phone_number: str) -> Dict:
        """Get information about current conversation"""
        state = self._get_conversation_state(phone_number)
        
        return {
            "stage": state["stage"],
            "service": state.get("service"),
            "date": state.get("date"),
            "time": state.get("time"),
            "ai_enabled": self.ai_enabled,
            "ai_provider": self.ai_agent.provider if self.ai_enabled else "rule_based"
        }
    
    # Delegate to original agent methods for booking operations
    def handle_payment_webhook(self, payment_intent_id: str) -> Optional[str]:
        """Handle Stripe payment webhook"""
        from agent.booking_agent import BookingAgent
        original_agent = BookingAgent()
        return original_agent.handle_payment_webhook(payment_intent_id)
    
    def send_reminder(self, appointment_id: str) -> str:
        """Send appointment reminder"""
        from agent.booking_agent import BookingAgent
        original_agent = BookingAgent()
        return original_agent.send_reminder(appointment_id)