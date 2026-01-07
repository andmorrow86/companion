"""
Appointment data model for managing bookings
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Literal
import json
import os

@dataclass
class Appointment:
    """Represents a massage appointment"""
    id: str
    client_phone: str
    service: str
    date: str  # YYYY-MM-DD format
    time: str  # HH:MM format
    duration: int  # minutes
    price: float
    deposit_amount: float
    deposit_paid: bool = False
    payment_status: Literal["pending", "deposit_paid", "fully_paid"] = "pending"
    status: Literal["pending", "confirmed", "completed", "cancelled", "no_show"] = "pending"
    payment_intent_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    notes: str = ""
    therapist_preference: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert appointment to dictionary for storage"""
        return {
            "id": self.id,
            "client_phone": self.client_phone,
            "service": self.service,
            "date": self.date,
            "time": self.time,
            "duration": self.duration,
            "price": self.price,
            "deposit_amount": self.deposit_amount,
            "deposit_paid": self.deposit_paid,
            "payment_status": self.payment_status,
            "status": self.status,
            "payment_intent_id": self.payment_intent_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "notes": self.notes,
            "therapist_preference": self.therapist_preference
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Appointment':
        """Create appointment from dictionary"""
        for field in ["created_at", "updated_at"]:
            if data.get(field):
                data[field] = datetime.fromisoformat(data[field])
        return cls(**data)

    def mark_deposit_paid(self, payment_intent_id: str):
        """Mark deposit as paid"""
        self.deposit_paid = True
        self.payment_status = "deposit_paid"
        self.payment_intent_id = payment_intent_id
        self.status = "confirmed"
        self.updated_at = datetime.now()

    def cancel(self):
        """Cancel the appointment"""
        self.status = "cancelled"
        self.updated_at = datetime.now()

    def complete(self):
        """Mark appointment as completed"""
        self.status = "completed"
        self.payment_status = "fully_paid"
        self.updated_at = datetime.now()

    def get_datetime(self) -> datetime:
        """Get appointment as datetime object"""
        return datetime.strptime(f"{self.date} {self.time}", "%Y-%m-%d %H:%M")


class AppointmentManager:
    """Manages appointment storage and retrieval"""
    
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.appointments_file = os.path.join(data_dir, "appointments.json")
        self._ensure_data_dir()
        self._load_appointments()

    def _ensure_data_dir(self):
        """Create data directory if it doesn't exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def _load_appointments(self):
        """Load appointments from file"""
        self.appointments = []
        if os.path.exists(self.appointments_file):
            try:
                with open(self.appointments_file, 'r') as f:
                    data = json.load(f)
                    self.appointments = [Appointment.from_dict(appt) for appt in data]
            except Exception as e:
                print(f"Error loading appointments: {e}")
                self.appointments = []

    def _save_appointments(self):
        """Save appointments to file"""
        try:
            data = [appt.to_dict() for appt in self.appointments]
            with open(self.appointments_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving appointments: {e}")

    def create_appointment(self, **kwargs) -> Appointment:
        """Create a new appointment"""
        import uuid
        kwargs["id"] = str(uuid.uuid4())
        appointment = Appointment(**kwargs)
        self.appointments.append(appointment)
        self._save_appointments()
        return appointment

    def update_appointment(self, appointment: Appointment):
        """Update an existing appointment"""
        for i, appt in enumerate(self.appointments):
            if appt.id == appointment.id:
                self.appointments[i] = appointment
                self._save_appointments()
                return

    def get_appointment_by_id(self, appointment_id: str) -> Optional[Appointment]:
        """Get appointment by ID"""
        for appt in self.appointments:
            if appt.id == appointment_id:
                return appt
        return None

    def get_client_appointments(self, phone_number: str) -> list[Appointment]:
        """Get all appointments for a client"""
        return [appt for appt in self.appointments if appt.client_phone == phone_number]

    def get_appointments_by_date(self, date: str) -> list[Appointment]:
        """Get all appointments for a specific date"""
        return [appt for appt in self.appointments if appt.date == date and appt.status != "cancelled"]

    def get_appointments_by_date_range(self, start_date: str, end_date: str) -> list[Appointment]:
        """Get appointments within a date range"""
        appointments = []
        for appt in self.appointments:
            if appt.status == "cancelled":
                continue
            if start_date <= appt.date <= end_date:
                appointments.append(appt)
        return appointments

    def check_availability(self, date: str, time: str, duration: int) -> bool:
        """Check if a time slot is available"""
        existing_appointments = self.get_appointments_by_date(date)
        
        start_time = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        end_time = start_time + datetime.timedelta(minutes=duration)
        
        for appt in existing_appointments:
            appt_start = datetime.strptime(f"{appt.date} {appt.time}", "%Y-%m-%d %H:%M")
            appt_end = appt_start + datetime.timedelta(minutes=appt.duration)
            
            # Check for overlap
            if not (end_time <= appt_start or start_time >= appt_end):
                return False
        
        return True

    def get_available_slots(self, date: str, opening_time: str, closing_time: str, 
                           slot_duration: int) -> list[str]:
        """Get available time slots for a given date"""
        import datetime as dt
        
        existing_appointments = self.get_appointments_by_date(date)
        booked_slots = set()
        
        # Mark booked time slots
        for appt in existing_appointments:
            appt_start = dt.datetime.strptime(f"{appt.date} {appt.time}", "%Y-%m-%d %H:%M")
            appt_end = appt_start + dt.timedelta(minutes=appt.duration)
            
            current = appt_start
            while current < appt_end:
                booked_slots.add(current.strftime("%H:%M"))
                current += dt.timedelta(minutes=slot_duration)

        # Generate all possible slots
        open_time = dt.datetime.strptime(opening_time, "%H:%M")
        close_time = dt.datetime.strptime(closing_time, "%H:%M")
        
        available_slots = []
        current = open_time
        while current + dt.timedelta(minutes=60) <= close_time:  # Minimum 60 min booking
            time_str = current.strftime("%H:%M")
            if time_str not in booked_slots:
                available_slots.append(time_str)
            current += dt.timedelta(minutes=slot_duration)
        
        return available_slots

    def cancel_appointment(self, appointment_id: str) -> bool:
        """Cancel an appointment"""
        appointment = self.get_appointment_by_id(appointment_id)
        if appointment:
            appointment.cancel()
            self._save_appointments()
            return True
        return False

    def get_upcoming_appointments(self) -> list[Appointment]:
        """Get all upcoming appointments"""
        now = datetime.now()
        upcoming = []
        for appt in self.appointments:
            if appt.status not in ["cancelled", "completed", "no_show"]:
                if appt.get_datetime() > now:
                    upcoming.append(appt)
        return sorted(upcoming, key=lambda x: x.get_datetime())