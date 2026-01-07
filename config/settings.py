"""
Configuration settings for the massage parlor booking agent
"""
import os
from datetime import time
from typing import List

# Business Settings
BUSINESS_NAME = "Serenity Massage Therapy"
BUSINESS_HOURS = {
    "monday": {"start": "09:00", "end": "20:00"},
    "tuesday": {"start": "09:00", "end": "20:00"},
    "wednesday": {"start": "09:00", "end": "20:00"},
    "thursday": {"start": "09:00", "end": "20:00"},
    "friday": {"start": "09:00", "end": "20:00"},
    "saturday": {"start": "10:00", "end": "18:00"},
    "sunday": {"start": "closed", "end": "closed"},
}

# Massage Services and Duration (in minutes)
SERVICES = {
    "swedish": {"name": "Swedish Massage", "duration": 60, "price": 80},
    "deep_tissue": {"name": "Deep Tissue Massage", "duration": 60, "price": 90},
    "hot_stone": {"name": "Hot Stone Therapy", "duration": 75, "price": 120},
    "aromatherapy": {"name": "Aromatherapy Massage", "duration": 60, "price": 95},
    "sports": {"name": "Sports Massage", "duration": 60, "price": 85},
    "couples": {"name": "Couples Massage", "duration": 90, "price": 200},
}

# Time Slot Configuration
SLOT_DURATION = 30  # minutes
MIN_BOOKING_ADVANCE = 2  # hours
MAX_BOOKING_ADVANCE = 30  # days

# Deposit Settings
DEPOSIT_ENABLED = True
DEPOSIT_AMOUNT = 20  # fixed amount in dollars
DEPOSIT_PERCENTAGE = 0.25  # 25% of service price
DEPOSIT_TYPE = "percentage"  # "fixed" or "percentage"
DEPOSIT_REQUIRED_FOR_SERVICES = ["hot_stone", "couples"]

# Payment Settings
STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY", "")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")

# SMS/Twilio Settings
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "")

# Message Templates
WELCOME_MESSAGE = f"Welcome to {BUSINESS_NAME}! 🌿 I'm here to help you book your perfect massage session. What type of massage are you interested in today?"

SERVICE_MENU = """Available massage services:
1. Swedish Massage (60 min) - $80
2. Deep Tissue Massage (60 min) - $90
3. Hot Stone Therapy (75 min) - $120
4. Aromatherapy Massage (60 min) - $95
5. Sports Massage (60 min) - $85
6. Couples Massage (90 min) - $200

Please reply with the number or service name you'd like to book."""

BOOKING_CONFIRMATION = """Your appointment has been confirmed! 🎉

Details:
- Service: {service}
- Date: {date}
- Time: {time}
- Duration: {duration} minutes
- Price: ${price}
- Deposit Paid: ${deposit}

We'll send you a reminder 24 hours before your appointment. See you soon!"""

DEPOSIT_REQUEST = """To secure your appointment, a ${deposit_amount} deposit is required.

This deposit will be applied to your total service cost and is fully refundable if you cancel at least 24 hours in advance.

Please use the following payment link to complete your deposit:
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