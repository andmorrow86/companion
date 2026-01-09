"""
Configuration settings for the personal assistant booking agent
"""
import os
from datetime import time
from typing import List

# Business Settings
BUSINESS_NAME = "Elite Personal Assistants"
BUSINESS_HOURS = {
    "monday": {"start": "08:00", "end": "20:00"},
    "tuesday": {"start": "08:00", "end": "20:00"},
    "wednesday": {"start": "08:00", "end": "20:00"},
    "thursday": {"start": "08:00", "end": "20:00"},
    "friday": {"start": "08:00", "end": "20:00"},
    "saturday": {"start": "09:00", "end": "18:00"},
    "sunday": {"start": "10:00", "end": "16:00"},
}

# Personal Assistant Services and Duration (in minutes)
SERVICES = {
    "general_assistance": {
        "name": "General Assistance",
        "duration": 60,
        "price": 50,
        "description": "Daily tasks, errands, scheduling assistance"
    },
    "administrative_support": {
        "name": "Administrative Support",
        "duration": 60,
        "price": 65,
        "description": "Document preparation, organization, filing"
    },
    "lifestyle_management": {
        "name": "Lifestyle Management",
        "duration": 90,
        "price": 85,
        "description": "Shopping coordination, travel planning"
    },
    "event_planning": {
        "name": "Event Planning",
        "duration": 120,
        "price": 150,
        "description": "Parties, gatherings, special occasions"
    },
    "concierge_services": {
        "name": "Concierge Services",
        "duration": 60,
        "price": 75,
        "description": "Reservations, appointments, research"
    },
    "senior_care_assistance": {
        "name": "Senior Care Assistance",
        "duration": 120,
        "price": 100,
        "description": "Companionship and basic support services"
    },
}

# Time Slot Configuration
SLOT_DURATION = 30  # minutes
MIN_BOOKING_ADVANCE = 4  # hours
MAX_BOOKING_ADVANCE = 30  # days

# Payment Settings
PAYMENT_ENABLED = True
PAYMENT_REQUIRED = True
PAYMENT_METHODS = ["credit_card", "debit_card", "bank_transfer"]

# Stripe Integration (for secure payments)
STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY", "")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")

# SMS/Twilio Settings
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "")

# Message Templates
WELCOME_MESSAGE = f"Welcome to {BUSINESS_NAME}! 🌟 I'm here to help you book the perfect personal assistant for your needs. What type of assistance are you looking for today?"

SERVICE_MENU = """Available personal assistant services:
1. General Assistance (60 min) - $50
   - Daily tasks, errands, scheduling assistance
   
2. Administrative Support (60 min) - $65
   - Document preparation, organization, filing
   
3. Lifestyle Management (90 min) - $85
   - Shopping coordination, travel planning
   
4. Event Planning (120 min) - $150
   - Parties, gatherings, special occasions
   
5. Concierge Services (60 min) - $75
   - Reservations, appointments, research
   
6. Senior Care Assistance (120 min) - $100
   - Companionship and basic support services

Please reply with the number or service name you'd like to book."""

BOOKING_CONFIRMATION = """Your appointment has been confirmed! 🎉

Details:
- Service: {service}
- Date: {date}
- Time: {time}
- Duration: {duration} minutes
- Price: ${price}

We'll send you a reminder 24 hours before your appointment. Our team is ready to assist you!"""

PAYMENT_REQUEST = """To secure your appointment, payment of ${amount} is required.

This payment will be applied to your total service cost.

Please use the following payment link to complete your booking:
{payment_link}

Once payment is received, your appointment will be confirmed."""

RESCHEDULE_REQUEST = "I'd be happy to help you reschedule. Please provide your preferred new date and time, and I'll check availability for you."

CANCELLATION_POLICY = """Cancellation Policy:
- Full refund if cancelled 24+ hours before appointment
- 50% refund if cancelled 12-24 hours before
- No refund for cancellations less than 12 hours before appointment

Would you like to proceed with cancellation?"""

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")