"""
Client data model for managing customer information
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
import json
import os

@dataclass
class Client:
    """Represents a massage parlor client"""
    phone_number: str
    name: Optional[str] = None
    email: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    preferences: dict = field(default_factory=dict)
    appointment_count: int = 0
    total_spent: float = 0.0
    notes: List[str] = field(default_factory=list)
    payment_methods: List[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert client to dictionary for storage"""
        return {
            "phone_number": self.phone_number,
            "name": self.name,
            "email": self.email,
            "created_at": self.created_at.isoformat(),
            "preferences": self.preferences,
            "appointment_count": self.appointment_count,
            "total_spent": self.total_spent,
            "notes": self.notes,
            "payment_methods": self.payment_methods
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Client':
        """Create client from dictionary"""
        if data.get("created_at"):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        return cls(**data)

    def add_preference(self, key: str, value: str):
        """Add or update a client preference"""
        self.preferences[key] = value

    def add_note(self, note: str):
        """Add a note to the client record"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.notes.append(f"{timestamp}: {note}")

    def add_payment_method(self, method_type: str, last_four: str):
        """Add a payment method to client record"""
        self.payment_methods.append({
            "type": method_type,
            "last_four": last_four,
            "added_at": datetime.now().isoformat()
        })

    def increment_appointments(self, amount: float):
        """Update appointment statistics"""
        self.appointment_count += 1
        self.total_spent += amount


class ClientManager:
    """Manages client data storage and retrieval"""
    
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.clients_file = os.path.join(data_dir, "clients.json")
        self._ensure_data_dir()
        self._load_clients()

    def _ensure_data_dir(self):
        """Create data directory if it doesn't exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def _load_clients(self):
        """Load clients from file"""
        self.clients = {}
        if os.path.exists(self.clients_file):
            try:
                with open(self.clients_file, 'r') as f:
                    data = json.load(f)
                    for phone, client_data in data.items():
                        self.clients[phone] = Client.from_dict(client_data)
            except Exception as e:
                print(f"Error loading clients: {e}")
                self.clients = {}

    def _save_clients(self):
        """Save clients to file"""
        try:
            data = {phone: client.to_dict() for phone, client in self.clients.items()}
            with open(self.clients_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving clients: {e}")

    def get_or_create_client(self, phone_number: str) -> Client:
        """Get existing client or create new one"""
        phone_number = phone_number.strip().replace("-", "").replace(" ", "")
        
        if phone_number not in self.clients:
            self.clients[phone_number] = Client(phone_number=phone_number)
            self._save_clients()
        
        return self.clients[phone_number]

    def update_client(self, client: Client):
        """Update client information"""
        self.clients[client.phone_number] = client
        self._save_clients()

    def get_client_by_phone(self, phone_number: str) -> Optional[Client]:
        """Get client by phone number"""
        phone_number = phone_number.strip().replace("-", "").replace(" ", "")
        return self.clients.get(phone_number)

    def search_clients(self, name: str) -> List[Client]:
        """Search clients by name"""
        name_lower = name.lower()
        return [
            client for client in self.clients.values()
            if client.name and name_lower in client.name.lower()
        ]