# Quick Start Guide

Get your personal assistant booking agent up and running in minutes!

## 🚀 Quick Setup

### 1. Install Dependencies
```bash
cd companion
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)
For full functionality with payments:
```bash
cp .env.example .env
# Edit .env and add your Stripe keys
```

### 3. Run Tests
```bash
python test_agent.py
```

### 4. Start the Server
```bash
python api/flask_app.py
```

The server will start on `http://localhost:5000`

## 📱 Using the Agent

### Option 1: API Integration

Send messages to the agent:

```bash
curl -X POST http://localhost:5000/message \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "5551234567",
    "message": "I want to book general assistance"
  }'
```

### Option 2: Interactive Demo

Run the interactive demo:
```bash
python demo.py
```

Select option 8 for interactive chat mode.

## 💬 Example Conversation

```
Client: Hi, I want to book a personal assistant

Agent: Welcome to Elite Personal Assistants! How can I help you today?

Client: What services do you offer?

Agent: [Displays service menu with prices]

Client: I'd like general assistance

Agent: Great choice! What date would you like to schedule your general assistance session?

Client: Tomorrow at 2pm

Agent: [Checks availability and confirms booking]
```

## 🔑 Key Features

- ✅ **Natural Language Processing** - Understands conversational messages
- ✅ **Smart Scheduling** - Automatic availability checking
- ✅ **Multiple Services** - General Assistance, Admin Support, Lifestyle Management, etc.
- ✅ **Payment Processing** - Optional Stripe integration for payments
- ✅ **Client Management** - Tracks preferences and history
- ✅ **Rescheduling & Cancellation** - Easy appointment management

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/message` | POST | Process client messages |
| `/services` | GET | Get available services |
| `/availability` | GET | Check availability |
| `/appointments/<phone>` | GET | Get client appointments |
| `/health` | GET | Health check |

## 🎯 Common Use Cases

### Check Availability
```bash
curl http://localhost:5000/availability?date=2024-01-15
```

### Get Services
```bash
curl http://localhost:5000/services
```

### Book Appointment
```bash
curl -X POST http://localhost:5000/message \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "5551234567",
    "message": "Book general assistance for tomorrow at 10am"
  }'
```

## ⚙️ Configuration

Edit `config/settings.py` to customize:
- Business name and hours
- Services and pricing
- Payment requirements
- Booking policies

## 🔍 Testing

Run the comprehensive test suite:
```bash
python test_agent.py
```

All tests should pass with green checkmarks.

## 📝 Next Steps

1. Set up Stripe account for payments (optional)
2. Configure business hours in settings.py
3. Integrate with your SMS service (Twilio recommended)
4. Customize services and pricing
5. Deploy to production

## 🛠️ Troubleshooting

**Port already in use?**
```bash
PORT=5001 python api/flask_app.py
```

**Stripe warnings?**
Normal if not configured. Agent works without payments.

**Import errors?**
Ensure you're in the `companion` directory.

## 📚 Full Documentation

See `README.md` for complete documentation.

## 🎉 You're Ready!

Your personal assistant booking agent is now running. Start processing client bookings automatically!