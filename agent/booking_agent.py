"""
Main booking agent that handles all client interactions
"""
from typing import Dict, Optional, List
from datetime import datetime
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.client import ClientManager
from models.appointment import AppointmentManager
from core.scheduler import Scheduler
from core.payment_processor import PaymentProcessor
from core.nlu import NLU
from config.settings import (
    DATA_DIR, LOGS_DIR, BOOKING_CONFIRMATION, WELCOME_MESSAGE,
    DEPOSIT_ENABLED
)


class BookingAgent:
    """Main agent that orchestrates the booking process"""
    
    def __init__(self):
        # Initialize managers
        self.client_manager = ClientManager(DATA_DIR)
        self.appointment_manager = AppointmentManager(DATA_DIR)
        self.scheduler = Scheduler(self.appointment_manager)
        self.payment_processor = PaymentProcessor()
        self.nlu = NLU()
        
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
                "messages": []
            }
        
        return self.conversations[phone_number]
    
    def _update_conversation_state(self, phone_number: str, updates: Dict):
        """Update conversation state"""
        state = self._get_conversation_state(phone_number)
        state.update(updates)
    
    def _reset_conversation(self, phone_number: str):
        """Reset conversation to initial state"""
        phone_number = phone_number.strip().replace("-", "").replace(" ", "")
        if phone_number in self.conversations:
            del self.conversations[phone_number]
    
    def _log_message(self, phone_number: str, message: str, is_client: bool = True):
        """Log messages for debugging and analysis"""
        log_file = os.path.join(LOGS_DIR, f"{phone_number}.log")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(log_file, 'a') as f:
            direction = "CLIENT" if is_client else "AGENT"
            f.write(f"[{timestamp}] {direction}: {message}\n")
    
    def process_message(self, phone_number: str, message: str) -> str:
        """
        Process an incoming message from a client
        
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
        
        # Parse the message
        intent, extracted_data = self.nlu.parse_booking_request(message)
        
        # Handle based on current stage
        response = self._handle_message(state, intent, extracted_data, message)
        
        # Log the response
        self._log_message(phone_number, response, is_client=False)
        
        return response
    
    def _handle_message(self, state: Dict, intent: str, extracted_data: Dict, original_message: str) -> str:
        """Handle message based on current conversation stage"""
        
        # Update extracted data
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
        
        stage = state["stage"]
        
        # Stage: greeting
        if stage == "greeting":
            if intent == "greeting":
                return self.nlu.get_response_for_intent("greeting")
            elif intent == "services":
                return self.nlu.get_response_for_intent("services")
            elif intent == "check_availability":
                return self._handle_check_availability(state, extracted_data)
            elif intent == "book":
                if state["service"]:
                    state["stage"] = "collecting_date"
                    return f"Great choice! What date would you like to schedule your {state['service']} massage?"
                else:
                    state["stage"] = "collecting_service"
                    return self.nlu.get_response_for_intent("book", {"service": None})
            else:
                state["stage"] = "collecting_service"
                return "I'd be happy to help you book an appointment! What type of massage would you like?"
        
        # Stage: collecting_service
        elif stage == "collecting_service":
            if intent == "book":
                if state["service"]:
                    state["stage"] = "collecting_date"
                    return f"Perfect! What date would you like to schedule your {state['service']} massage?"
                else:
                    return self.nlu.get_response_for_intent("services")
            else:
                service = self.nlu.extract_service(original_message)
                if service:
                    state["service"] = service
                    state["stage"] = "collecting_date"
                    return f"Great! What date would you like to schedule your {service} massage?"
                else:
                    return "I didn't catch which service you'd like. Please choose from: Swedish, Deep Tissue, Hot Stone, Aromatherapy, Sports, or Couples massage."
        
        # Stage: collecting_date
        elif stage == "collecting_date":
            if state["date"]:
                state["stage"] = "collecting_time"
                available_slots = self.scheduler.get_available_slots(state["date"])
                if available_slots:
                    slots_str = ", ".join([self.scheduler.format_time_display(slot) for slot in available_slots[:5]])
                    return f"Available times for {self.scheduler.format_date_display(state['date'])}: {slots_str}. What time works best for you?"
                else:
                    return f"Unfortunately, we don't have any availability on {self.scheduler.format_date_display(state['date'])}. Would you like to check another date?"
            else:
                return "What date would you like to schedule your appointment? You can say things like 'tomorrow', 'next Monday', or give a specific date like 'January 15'."
        
        # Stage: collecting_time
        elif stage == "collecting_time":
            if state["time"]:
                # Validate the appointment
                is_valid, error_msg = self.scheduler.validate_appointment_request(
                    state["date"], state["time"], state["service"]
                )
                
                if not is_valid:
                    # Suggest alternatives
                    alternatives = self.scheduler.suggest_alternative_times(state["date"], state["time"])
                    if alternatives:
                        alt_str = ", ".join([self.scheduler.format_time_display(slot) for slot in alternatives[:3]])
                        return f"{error_msg}\n\nAvailable alternatives: {alt_str}"
                    return error_msg
                
                # Check if deposit is required
                service_info = self.scheduler.get_service_info(state["service"])
                deposit_amount = self.scheduler.calculate_deposit(state["service"], service_info["price"])
                
                if deposit_amount > 0 and DEPOSIT_ENABLED:
                    state["stage"] = "awaiting_deposit"
                    return f"I can book your {service_info['name']} on {self.scheduler.format_date_display(state['date'])} at {self.scheduler.format_time_display(state['time'])}.\n\nA ${deposit_amount} deposit is required to confirm this appointment. Would you like to proceed with the deposit?"
                else:
                    # Create appointment directly
                    return self._create_appointment(state)
            
            else:
                available_slots = self.scheduler.get_available_slots(state["date"])
                if available_slots:
                    slots_str = ", ".join([self.scheduler.format_time_display(slot) for slot in available_slots[:5]])
                    return f"What time would you prefer? Available slots: {slots_str}"
                else:
                    return "No time slots available. Would you like to try a different date?"
        
        # Stage: awaiting_deposit
        elif stage == "awaiting_deposit":
            if "yes" in original_message.lower() or "proceed" in original_message.lower():
                # Create appointment first
                appointment = self._create_appointment_record(state)
                state["appointment_id"] = appointment.id
                
                # Handle deposit
                service_info = self.scheduler.get_service_info(state["service"])
                deposit_amount = self.scheduler.calculate_deposit(state["service"], service_info["price"])
                
                try:
                    deposit_info = self.payment_processor.handle_deposit_requirement(
                        state["service"], service_info["price"], appointment.id, state["client"].email
                    )
                    
                    if deposit_info.get("payment_url"):
                        state["payment_intent_id"] = deposit_info.get("payment_intent_id")
                        return deposit_info["message"]
                    else:
                        return f"Error creating payment link: {deposit_info.get('error', 'Unknown error')}"
                
                except Exception as e:
                    return f"Sorry, there was an error setting up the deposit: {str(e)}"
            
            elif "no" in original_message.lower():
                state["stage"] = "collecting_time"
                return "No problem! Would you like to choose a different time or service?"
            
            else:
                return "Please let me know if you'd like to proceed with the deposit (yes/no)."
        
        # Stage: confirmed
        elif stage == "confirmed":
            if intent == "reschedule":
                return self._handle_reschedule(state, original_message)
            elif intent == "cancel":
                return self._handle_cancellation(state, original_message)
            else:
                return "Your appointment is confirmed! Is there anything else I can help you with?"
        
        # Handle other intents
        if intent == "services":
            return self.nlu.get_response_for_intent("services")
        elif intent == "pricing":
            return self.nlu.get_response_for_intent("pricing")
        elif intent == "hours":
            return self.nlu.get_response_for_intent("hours")
        elif intent == "help":
            return self.nlu.get_response_for_intent("help")
        elif intent == "check_availability":
            return self._handle_check_availability(state, extracted_data)
        
        return "I'm here to help! Would you like to book an appointment, check our services, or ask about availability?"
    
    def _handle_check_availability(self, state: Dict, extracted_data: Dict) -> str:
        """Handle availability check requests"""
        if extracted_data.get("date"):
            date = extracted_data["date"]
            available_slots = self.scheduler.get_available_slots(date)
            
            if available_slots:
                slots_str = ", ".join([self.scheduler.format_time_display(slot) for slot in available_slots[:8]])
                return f"Available times for {self.scheduler.format_date_display(date)}: {slots_str}"
            else:
                available_dates = self.scheduler.get_available_dates(14)
                dates_str = ", ".join([self.scheduler.format_date_display(date) for date in available_dates[:5]])
                return f"No availability on {self.scheduler.format_date_display(date)}. We have openings on: {dates_str}"
        else:
            available_dates = self.scheduler.get_available_dates(14)
            dates_str = ", ".join([self.scheduler.format_date_display(date) for date in available_dates[:7]])
            return f"Here are our available dates in the next 2 weeks: {dates_str}\n\nWhich date would you like to check?"
    
    def _create_appointment_record(self, state: Dict):
        """Create the appointment record"""
        service_info = self.scheduler.get_service_info(state["service"])
        
        deposit_amount = self.scheduler.calculate_deposit(state["service"], service_info["price"])
        
        appointment = self.appointment_manager.create_appointment(
            client_phone=state["client"].phone_number,
            service=state["service"],
            date=state["date"],
            time=state["time"],
            duration=service_info["duration"],
            price=service_info["price"],
            deposit_amount=deposit_amount,
            payment_status="pending" if deposit_amount > 0 else "fully_paid",
            status="confirmed" if deposit_amount == 0 else "pending"
        )
        
        # Update client info
        self.client_manager.update_client(state["client"])
        
        return appointment
    
    def _create_appointment(self, state: Dict) -> str:
        """Create appointment and return confirmation"""
        appointment = self._create_appointment_record(state)
        state["appointment_id"] = appointment.id
        state["stage"] = "confirmed"
        
        service_info = self.scheduler.get_service_info(state["service"])
        
        confirmation = BOOKING_CONFIRMATION.format(
            service=service_info['name'],
            date=self.scheduler.format_date_display(state['date']),
            time=self.scheduler.format_time_display(state['time']),
            duration=service_info['duration'],
            price=service_info['price'],
            deposit=appointment.deposit_amount
        )
        
        return confirmation
    
    def _handle_reschedule(self, state: Dict, message: str) -> str:
        """Handle reschedule requests"""
        if not state.get("appointment_id"):
            # Find upcoming appointments for this client
            appointments = self.appointment_manager.get_client_appointments(
                state["client"].phone_number
            )
            upcoming = [a for a in appointments if a.status in ["pending", "confirmed"]]
            
            if not upcoming:
                return "You don't have any upcoming appointments to reschedule."
            
            # Use the most recent one
            state["appointment_id"] = upcoming[0].id
        
        # Extract new date/time
        new_date = self.nlu.extract_date(message)
        new_time = self.nlu.extract_time(message)
        
        if not new_date or not new_time:
            return "To reschedule, please provide the new date and time. For example: 'I'd like to reschedule to tomorrow at 3pm'"
        
        # Validate new time
        is_valid, error_msg = self.scheduler.validate_appointment_request(
            new_date, new_time, state["service"]
        )
        
        if not is_valid:
            return error_msg
        
        # Update appointment
        appointment = self.appointment_manager.get_appointment_by_id(state["appointment_id"])
        if appointment:
            appointment.date = new_date
            appointment.time = new_time
            self.appointment_manager.update_appointment(appointment)
            
            service_info = self.scheduler.get_service_info(state["service"])
            return f"Your appointment has been rescheduled to {self.scheduler.format_date_display(new_date)} at {self.scheduler.format_time_display(new_time)}.\n\nService: {service_info['name']}\nDuration: {service_info['duration']} minutes"
        
        return "Unable to reschedule appointment. Please contact us directly."
    
    def _handle_cancellation(self, state: Dict, message: str) -> str:
        """Handle cancellation requests"""
        if not state.get("appointment_id"):
            # Find upcoming appointments for this client
            appointments = self.appointment_manager.get_client_appointments(
                state["client"].phone_number
            )
            upcoming = [a for a in appointments if a.status in ["pending", "confirmed"]]
            
            if not upcoming:
                return "You don't have any upcoming appointments to cancel."
            
            # Use the most recent one
            state["appointment_id"] = upcoming[0].id
        
        appointment = self.appointment_manager.get_appointment_by_id(state["appointment_id"])
        if not appointment:
            return "Unable to find your appointment."
        
        # Check cancellation policy
        appointment_datetime = appointment.get_datetime()
        now = datetime.now()
        hours_until = (appointment_datetime - now).total_seconds() / 3600
        
        if hours_until >= 24:
            refund_amount = appointment.deposit_amount
        elif hours_until >= 12:
            refund_amount = appointment.deposit_amount * 0.5
        else:
            refund_amount = 0
        
        # Process cancellation
        if "yes" in message.lower() or "confirm" in message.lower():
            appointment.cancel()
            self.appointment_manager.update_appointment(appointment)
            
            # Process refund if applicable
            if refund_amount > 0 and appointment.payment_intent_id:
                self.payment_processor.create_refund(appointment.payment_intent_id)
            
            refund_msg = f"You will receive a ${refund_amount:.2f} refund." if refund_amount > 0 else "No refund will be issued."
            
            state["stage"] = "greeting"
            return f"Your appointment has been cancelled. {refund_msg}\n\nWould you like to book another appointment?"
        else:
            from config.settings import CANCELLATION_POLICY
            refund_info = f"\n\nIf cancelled now, you will receive a ${refund_amount:.2f} refund."
            return CANCELLATION_POLICY + refund_info
    
    def handle_payment_webhook(self, payment_intent_id: str) -> Optional[str]:
        """
        Handle Stripe payment webhook
        
        Returns:
            Phone number of client to notify, or None
        """
        # Find appointment with this payment intent
        for appt in self.appointment_manager.appointments:
            if appt.payment_intent_id == payment_intent_id:
                appt.mark_deposit_paid(payment_intent_id)
                self.appointment_manager.update_appointment(appt)
                return appt.client_phone
        
        return None
    
    def send_reminder(self, appointment_id: str) -> str:
        """Send appointment reminder"""
        appointment = self.appointment_manager.get_appointment_by_id(appointment_id)
        if not appointment:
            return ""
        
        service_info = self.scheduler.get_service_info(appointment.service)
        
        reminder = f"""Reminder: Your massage appointment is tomorrow! 🌿

Service: {service_info['name']}
Date: {self.scheduler.format_date_display(appointment.date)}
Time: {self.scheduler.format_time_display(appointment.time)}
Duration: {service_info['duration']} minutes

We look forward to seeing you!"""
        
        return reminder