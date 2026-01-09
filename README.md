# Personal Assistant Booking Agent

A comprehensive AI-powered booking and scheduling agent for personal assistant services. This system handles client text messages, manages appointments, processes payments, and provides automated customer service.

## Features

### 🌟 Core Capabilities
- **Natural Language Processing**: Understands conversational booking requests
- **Appointment Scheduling**: Intelligent time slot management and availability checking
- **Payment Processing**: Secure payment collection via Stripe integration
- **Client Management**: Track client preferences and history
- **Automated Responses**: Context-aware conversation handling
- **Multi-Service Support**: General Assistance, Administrative Support, Lifestyle Management, Event Planning, Concierge Services, and Senior Care Assistance

### 📱 Communication Features
- Process text messages from clients
- Handle booking inquiries
- Provide service information
- Send appointment confirmations
- Process cancellations and rescheduling
- Send appointment reminders

### 💳 Payment Features
- Stripe integration for secure payments
- Automatic payment processing
- Payment verification
- Receipt generation

## Installation

### Prerequisites
- Python 3.11 or higher
- pip package manager
- Stripe account (for payments)
- Twilio account (for SMS - optional)

### Setup Instructions

1. **Clone or download the project**

2. **Install dependencies**
```bash
cd companion
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
```

Edit `.env` and add your configuration:
```env
STRIPE_PUBLIC_KEY="your_stripe_public_key"
STRIPE_SECRET_KEY="your_stripe_secret_key"
BUSINESS_NAME="Your Business Name"
```

4. **Run the application**
```bash
python api/flask_app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Message Processing
- `POST /message` - Process incoming client messages
  ```json
  {
    "phone_number": "1234567890",
    "message": "I'd like to book general assistance"
  }
  ```

### Availability
- `GET /availability` - Check available dates
- `GET /availability?date=2024-01-15` - Check time slots for specific date

### Services
- `GET /services` - Get list of available services

### Appointments
- `GET /appointments/<phone_number>` - Get client's appointments
- `POST /appointments/<appointment_id>/cancel` - Cancel an appointment

### Clients
- `GET /clients/<phone_number>` - Get client information

### Admin
- `GET /admin/upcoming` - Get all upcoming appointments

### Webhooks
- `POST /webhook/stripe` - Handle Stripe payment webhooks

## Usage Examples

### Basic Booking Flow

**Client**: "Hi, I'd like to book a personal assistant"

**Agent**: "Welcome to Elite Personal Assistants! 🌟 How can I help you today? You can book an appointment, check our services, or ask about availability."

**Client**: "What services do you offer?"

**Agent**: (Displays service menu with prices)

**Client**: "I'd like general assistance"

**Agent**: "Great choice! What date would you like to schedule your general assistance session?"

**Client**: "Tomorrow at 2pm"

**Agent**: (Checks availability, confirms booking, requests payment if needed)

### Checking Availability

```bash
curl http://localhost:5000/availability?date=2024-01-15
```

Response:
```json
{
  "success": true,
  "date": "2024-01-15",
  "available_slots": ["09:00", "09:30", "10:00", "10:30", "11:00"]
}
```

### Processing a Message

```bash
curl -X POST http://localhost:5000/message \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "1234567890",
    "message": "I want to book general assistance tomorrow at 10am"
  }'
```

## Configuration

### Business Settings (config/settings.py)

Edit these settings to customize for your business:

```python
BUSINESS_NAME = "Your Business Name"
BUSINESS_HOURS = {
    "monday": {"start": "08:00", "end": "20:00"},
    # ... other days
}

SERVICES = {
    "general_assistance": {
        "name": "General Assistance",
        "duration": 60,
        "price": 50
    },
    # ... other services
}
```

### Payment Configuration

Configure payment processing:
- Stripe integration for secure payments
- Automatic payment verification
- Support for multiple payment methods

## Project Structure

```
companion/
├── agent/
│   └── booking_agent.py       # Main agent logic
├── api/
│   └── flask_app.py           # Flask API server
├── config/
│   └── settings.py            # Configuration settings
├── core/
│   ├── nlu.py                 # Natural language understanding
│   ├── payment_processor.py   # Payment handling
│   └── scheduler.py           # Scheduling logic
├── models/
│   ├── appointment.py         # Appointment data model
│   └── client.py              # Client data model
├── data/                      # Data storage (auto-created)
├── logs/                      # Message logs (auto-created)
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
└── README.md                 # This file
```

## Services Offered

1. **General Assistance** (60 min) - $50
   - Daily tasks, errands, scheduling assistance

2. **Administrative Support** (60 min) - $65
   - Document preparation, organization, filing

3. **Lifestyle Management** (90 min) - $85
   - Shopping coordination, travel planning

4. **Event Planning** (120 min) - $150
   - Parties, gatherings, special occasions

5. **Concierge Services** (60 min) - $75
   - Reservations, appointments, research

6. **Senior Care Assistance** (120 min) - $100
   - Companionship and basic support services

## Features in Detail

### Natural Language Understanding
The agent understands:
- Service preferences ("general assistance", "administrative support", "lifestyle management")
- Date formats ("tomorrow", "next Monday", "January 15")
- Time formats ("2pm", "14:00", "3:30 PM")
- Intent classification (booking, cancellation, rescheduling)
- Client information (names, emails)

### Scheduling System
- Business hours management
- Conflict detection
- Time slot validation
- Availability checking
- Booking window restrictions

### Payment Processing
- Stripe integration
- Payment link generation
- Payment verification
- Refund processing

### Client Management
- Client profiles
- Preference tracking
- Appointment history
- Payment method storage
- Notes and communications

## Testing

You can test the agent using the API:

```bash
# Start the server
python api/flask_app.py

# Test message processing
curl -X POST http://localhost:5000/message \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "5551234567",
    "message": "Hi, I'd like to book a personal assistant"
  }'
```

## Security Considerations

1. **API Security**: Implement authentication for production use
2. **Payment Security**: Use Stripe's webhook signatures
3. **Data Protection**: Encrypt sensitive client data
4. **Rate Limiting**: Implement rate limiting on API endpoints
5. **Environment Variables**: Never commit `.env` file to version control

## Deployment

### Using expose-port (Development)
```bash
# Start the server
python api/flask_app.py

# Expose the port
expose-port 5000
```

### Production Deployment
For production deployment:
1. Use a production WSGI server (Gunicorn, uWSGI)
2. Configure a reverse proxy (Nginx)
3. Set up SSL certificates
4. Configure environment variables
5. Set up database backup
6. Implement monitoring and logging

## Troubleshooting

### Common Issues

**Issue**: Stripe payment not working
- **Solution**: Check your Stripe API keys in `.env`

**Issue**: Appointments not being saved
- **Solution**: Ensure `data/` directory has write permissions

**Issue**: Agent not understanding messages
- **Solution**: Check logs in `logs/` directory for details

## Support

For issues or questions:
1. Check the logs in the `logs/` directory
2. Review the configuration in `config/settings.py`
3. Ensure all dependencies are installed
4. Verify environment variables are set correctly

## License

This project is provided as-is for use in legitimate personal assistant service businesses.

## Credits

Built with:
- Flask - Web framework
- Stripe - Payment processing
- Python 3.11 - Programming language
- Pydantic - Data validation