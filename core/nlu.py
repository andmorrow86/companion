"""
Natural Language Understanding module for processing client messages
"""
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from config.settings import SERVICES


class NLU:
    """Handles natural language understanding for booking requests"""
    
    def __init__(self):
        self.intents = {
            "book": ["book", "schedule", "appointment", "reserve", "make a booking"],
            "reschedule": ["reschedule", "change", "move", "different time"],
            "cancel": ["cancel", "not coming", "won't make it"],
            "check_availability": ["available", "what times", "when are you open", "slots"],
            "services": ["services", "what do you offer", "types of massage", "menu"],
            "pricing": ["price", "how much", "cost", "rates"],
            "hours": ["hours", "open", "when are you open", "business hours"],
            "deposit": ["deposit", "payment", "pay", "secure"],
            "help": ["help", "what can you do", "options", "menu"],
            "greeting": ["hi", "hello", "hey", "good morning", "good afternoon"]
        }
        
        self.service_keywords = {
            "swedish": ["swedish", "relaxing", "gentle"],
            "deep_tissue": ["deep tissue", "deep", "intense", "firm"],
            "hot_stone": ["hot stone", "stones", "heat"],
            "aromatherapy": ["aromatherapy", "aroma", "scent", "essential oils"],
            "sports": ["sports", "athlete", "injury", "recovery"],
            "couples": ["couples", "together", "romantic", "two people"]
        }

    def classify_intent(self, message: str) -> str:
        """
        Classify the intent of a user message
        
        Returns:
            The detected intent
        """
        message_lower = message.lower()
        
        # Check for greeting first
        for greeting in self.intents["greeting"]:
            if greeting in message_lower:
                return "greeting"
        
        # Check for other intents
        for intent, keywords in self.intents.items():
            if intent == "greeting":
                continue
            for keyword in keywords:
                if keyword in message_lower:
                    return intent
        
        # Default to book if no intent detected
        return "book"

    def extract_service(self, message: str) -> Optional[str]:
        """
        Extract the service type from a message
        
        Returns:
            Service key or None
        """
        message_lower = message.lower()
        
        for service, keywords in self.service_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    return service
        
        return None

    def extract_date(self, message: str) -> Optional[str]:
        """
        Extract date from a message
        
        Returns:
            Date in YYYY-MM-DD format or None
        """
        message_lower = message.lower()
        
        # Today, tomorrow, etc.
        today = datetime.now()
        
        if "today" in message_lower:
            return today.strftime("%Y-%m-%d")
        elif "tomorrow" in message_lower:
            return (today + timedelta(days=1)).strftime("%Y-%m-%d")
        elif "next week" in message_lower:
            return (today + timedelta(days=7)).strftime("%Y-%m-%d")
        
        # Day of week
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        for i, day in enumerate(days):
            if day in message_lower:
                days_ahead = i - today.weekday()
                if days_ahead <= 0:
                    days_ahead += 7
                return (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
        
        # Specific date patterns
        # MM/DD/YYYY or MM-DD-YYYY
        date_pattern = r'(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})'
        match = re.search(date_pattern, message)
        if match:
            month, day, year = match.groups()
            try:
                date = datetime.strptime(f"{month}/{day}/{year}", "%m/%d/%Y")
                return date.strftime("%Y-%m-%d")
            except ValueError:
                pass
        
        # Month day (e.g., "January 15")
        month_pattern = r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})(?:st|nd|rd|th)?'
        match = re.search(month_pattern, message_lower)
        if match:
            month_name, day = match.groups()
            try:
                date_str = f"{month_name} {day} {today.year}"
                date = datetime.strptime(date_str, "%B %d %Y")
                # If date is in the past, assume next year
                if date < today:
                    date = datetime.strptime(f"{month_name} {day} {today.year + 1}", "%B %d %Y")
                return date.strftime("%Y-%m-%d")
            except ValueError:
                pass
        
        return None

    def extract_time(self, message: str) -> Optional[str]:
        """
        Extract time from a message
        
        Returns:
            Time in HH:MM format or None
        """
        message_lower = message.lower()
        
        # HH:MM or HH:MM AM/PM
        time_pattern = r'(\d{1,2}):(\d{2})\s*(am|pm|a\.m\.|p\.m\.)?'
        match = re.search(time_pattern, message_lower)
        if match:
            hour, minute, period = match.groups()
            hour = int(hour)
            minute = int(minute)
            
            if period and "pm" in period:
                if hour != 12:
                    hour += 12
            elif period and "am" in period:
                if hour == 12:
                    hour = 0
            elif not period:
                # Assume 24-hour format if hour > 12
                pass
            
            return f"{hour:02d}:{minute:02d}"
        
        # HH AM/PM
        time_pattern = r'(\d{1,2})\s*(am|pm|a\.m\.|p\.m\.)'
        match = re.search(time_pattern, message_lower)
        if match:
            hour, period = match.groups()
            hour = int(hour)
            
            if "pm" in period:
                if hour != 12:
                    hour += 12
            elif "am" in period and hour == 12:
                hour = 0
            
            return f"{hour:02d}:00"
        
        return None

    def extract_name(self, message: str) -> Optional[str]:
        """
        Extract a name from a message
        
        Returns:
            Name or None
        """
        # This is a simple implementation - in production, you'd use NER
        message_lower = message.lower()
        words = message.split()
        
        # Look for "my name is" or "I'm" patterns
        patterns = [
            r"my name is\s+(\w+)",
            r"i['']m\s+(\w+)",
            r"i am\s+(\w+)",
            r"name['']s\s+(\w+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message_lower)
            if match:
                name = match.group(1).capitalize()
                # Check if there's a last name
                name_index = message_lower.find(name.lower())
                remaining = message[name_index + len(name):].strip()
                if remaining and remaining[0].isalpha():
                    return f"{name} {remaining.split()[0].capitalize()}"
                return name
        
        return None

    def extract_email(self, message: str) -> Optional[str]:
        """
        Extract email from a message
        
        Returns:
            Email address or None
        """
        email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        match = re.search(email_pattern, message)
        return match.group(0) if match else None

    def extract_booking_details(self, message: str) -> Dict[str, any]:
        """
        Extract all booking details from a message
        
        Returns:
            Dictionary with extracted information
        """
        return {
            "service": self.extract_service(message),
            "date": self.extract_time(message),
            "time": self.extract_time(message),
            "name": self.extract_name(message),
            "email": self.extract_email(message)
        }

    def parse_booking_request(self, message: str) -> Tuple[str, Dict[str, any]]:
        """
        Parse a booking request and return intent and extracted data
        
        Returns:
            Tuple of (intent, extracted_data)
        """
        intent = self.classify_intent(message)
        extracted_data = self.extract_booking_details(message)
        
        return intent, extracted_data

    def get_response_for_intent(self, intent: str, context: Dict[str, any] = None) -> str:
        """
        Get an appropriate response for a given intent
        
        Returns:
            Response message
        """
        from config.settings import (
            BUSINESS_NAME, BUSINESS_HOURS, SERVICES, SERVICE_MENU,
            BOOKING_CONFIRMATION, RESCHEDULE_REQUEST, CANCELLATION_POLICY
        )
        
        context = context or {}
        
        if intent == "greeting":
            return f"Welcome to {BUSINESS_NAME}! 🌿 How can I help you today? You can book an appointment, check our services, or ask about availability."
        
        elif intent == "services":
            return SERVICE_MENU
        
        elif intent == "pricing":
            price_info = "Here are our prices:\n\n"
            for key, info in SERVICES.items():
                price_info += f"• {info['name']}: ${info['price']}\n"
            return price_info
        
        elif intent == "hours":
            hours_info = f"Our business hours:\n\n"
            for day, hours in BUSINESS_HOURS.items():
                if hours['start'] == "closed":
                    hours_info += f"• {day.capitalize()}: Closed\n"
                else:
                    hours_info += f"• {day.capitalize()}: {hours['start']} - {hours['end']}\n"
            return hours_info
        
        elif intent == "check_availability":
            if context.get("date"):
                return f"Let me check availability for {context['date']}. Please wait while I retrieve the available slots..."
            else:
                return "What date would you like to check availability for? I can show you available time slots for the next 2 weeks."
        
        elif intent == "book":
            if not context.get("service"):
                return "I'd be happy to help you book an appointment! What type of massage would you like? You can choose from: Swedish, Deep Tissue, Hot Stone, Aromatherapy, Sports, or Couples massage."
            elif not context.get("date"):
                return f"Great choice! What date would you like to schedule your {context['service']} massage?"
            elif not context.get("time"):
                return f"What time would you prefer on {context['date']}?"
            else:
                return f"Perfect! Let me check if {context['date']} at {context['time']} is available for a {context['service']} massage..."
        
        elif intent == "reschedule":
            return RESCHEDULE_REQUEST
        
        elif intent == "cancel":
            if context.get("appointment"):
                return CANCELLATION_POLICY
            else:
                return "I can help you cancel your appointment. Please provide your phone number so I can look up your booking."
        
        elif intent == "help":
            return f"""I can help you with:
• Booking a new appointment
• Checking availability for specific dates
• Viewing our services and pricing
• Rescheduling or canceling appointments
• Payment and deposit information

What would you like to do?"""
        
        else:
            return "I'm here to help! You can ask me to book an appointment, check our services, or check availability. What would you like to know?"