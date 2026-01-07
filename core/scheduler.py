"""
Scheduler module for managing appointment availability and time slots
"""
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import calendar
from config.settings import BUSINESS_HOURS, SERVICES, SLOT_DURATION, MIN_BOOKING_ADVANCE, MAX_BOOKING_ADVANCE


class Scheduler:
    """Handles scheduling logic and availability management"""
    
    def __init__(self, appointment_manager):
        self.appointment_manager = appointment_manager

    def is_business_day(self, date: datetime) -> bool:
        """Check if a given date is a business day"""
        day_name = date.strftime("%A").lower()
        return BUSINESS_HOURS.get(day_name, {}).get("start") != "closed"

    def get_business_hours(self, date: datetime) -> Tuple[str, str]:
        """Get business hours for a given date"""
        day_name = date.strftime("%A").lower()
        hours = BUSINESS_HOURS.get(day_name, {})
        return hours.get("start", "09:00"), hours.get("end", "20:00")

    def is_valid_booking_time(self, requested_datetime: datetime) -> bool:
        """Check if the requested time is within allowed booking window"""
        now = datetime.now()
        min_time = now + timedelta(hours=MIN_BOOKING_ADVANCE)
        max_time = now + timedelta(days=MAX_BOOKING_ADVANCE)
        
        return min_time <= requested_datetime <= max_time

    def is_within_business_hours(self, requested_datetime: datetime) -> bool:
        """Check if the requested time is within business hours"""
        if not self.is_business_day(requested_datetime):
            return False
        
        opening, closing = self.get_business_hours(requested_datetime)
        opening_time = datetime.strptime(opening, "%H:%M").time()
        closing_time = datetime.strptime(closing, "%H:%M").time()
        requested_time = requested_datetime.time()
        
        return opening_time <= requested_time < closing_time

    def get_available_slots(self, date_str: str) -> List[str]:
        """Get available time slots for a given date"""
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return []
        
        if not self.is_business_day(date):
            return []
        
        opening, closing = self.get_business_hours(date)
        return self.appointment_manager.get_available_slots(
            date_str, opening, closing, SLOT_DURATION
        )

    def get_available_dates(self, days_ahead: int = 14) -> List[str]:
        """Get list of available dates for booking"""
        available_dates = []
        now = datetime.now()
        
        for i in range(days_ahead):
            date = now + timedelta(days=i+1)
            if self.is_business_day(date):
                date_str = date.strftime("%Y-%m-%d")
                slots = self.get_available_slots(date_str)
                if slots:
                    available_dates.append(date_str)
        
        return available_dates

    def validate_appointment_request(self, date: str, time: str, service: str) -> Tuple[bool, str]:
        """
        Validate an appointment request
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if service exists
        if service not in SERVICES:
            return False, f"Service '{service}' is not available. Please choose from our available services."
        
        service_info = SERVICES[service]
        duration = service_info["duration"]
        
        # Validate date format
        try:
            appointment_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        except ValueError:
            return False, "Invalid date or time format. Please use YYYY-MM-DD for date and HH:MM for time (e.g., 2024-01-15 14:30)"
        
        # Check if it's a business day
        if not self.is_business_day(appointment_datetime):
            return False, f"We're closed on {appointment_datetime.strftime('%A')}. Please choose a different day."
        
        # Check if within booking window
        if not self.is_valid_booking_time(appointment_datetime):
            return False, f"Appointments must be booked {MIN_BOOKING_ADVANCE} hours to {MAX_BOOKING_ADVANCE} days in advance."
        
        # Check if within business hours
        if not self.is_within_business_hours(appointment_datetime):
            opening, closing = self.get_business_hours(appointment_datetime)
            return False, f"Appointment time must be between {opening} and {closing} on business days."
        
        # Check availability
        if not self.appointment_manager.check_availability(date, time, duration):
            return False, "This time slot is not available. Please choose a different time."
        
        return True, ""

    def calculate_deposit(self, service: str, price: float) -> float:
        """Calculate required deposit amount"""
        from config.settings import (
            DEPOSIT_ENABLED, DEPOSIT_AMOUNT, DEPOSIT_PERCENTAGE, 
            DEPOSIT_TYPE, DEPOSIT_REQUIRED_FOR_SERVICES
        )
        
        if not DEPOSIT_ENABLED:
            return 0.0
        
        # Check if deposit is required for this service
        if service not in DEPOSIT_REQUIRED_FOR_SERVICES:
            return 0.0
        
        if DEPOSIT_TYPE == "fixed":
            return DEPOSIT_AMOUNT
        else:
            return round(price * DEPOSIT_PERCENTAGE, 2)

    def get_next_available_slot(self, date: str, preferred_time: str = None) -> str:
        """Get the next available time slot, trying preferred time first"""
        available_slots = self.get_available_slots(date)
        
        if not available_slots:
            return None
        
        if preferred_time and preferred_time in available_slots:
            return preferred_time
        
        return available_slots[0]

    def suggest_alternative_times(self, date: str, time: str, count: int = 3) -> List[str]:
        """Suggest alternative time slots if requested time is unavailable"""
        available_slots = self.get_available_slots(date)
        
        # Find slots close to the requested time
        if time in available_slots:
            return [time]
        
        # Sort available slots by proximity to requested time
        try:
            requested_minutes = int(time.split(":")[0]) * 60 + int(time.split(":")[1])
            
            def slot_distance(slot):
                slot_minutes = int(slot.split(":")[0]) * 60 + int(slot.split(":")[1])
                return abs(slot_minutes - requested_minutes)
            
            available_slots.sort(key=slot_distance)
        except:
            pass
        
        return available_slots[:count]

    def format_date_display(self, date_str: str) -> str:
        """Format date for display"""
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            return date.strftime("%A, %B %d, %Y")
        except ValueError:
            return date_str

    def format_time_display(self, time_str: str) -> str:
        """Format time for display"""
        try:
            time_obj = datetime.strptime(time_str, "%H:%M")
            return time_obj.strftime("%I:%M %p")
        except ValueError:
            return time_str

    def get_service_info(self, service: str) -> dict:
        """Get service information"""
        return SERVICES.get(service, {})

    def get_all_services(self) -> Dict[str, dict]:
        """Get all available services"""
        return SERVICES