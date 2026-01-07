# AI Integration Guide - Massage Parlor Booking Agent

## 🤖 Overview

The Massage Parlor Booking Agent now supports integration with AI providers (OpenAI GPT and Grok) for enhanced, natural conversations. This guide covers setup, configuration, and usage of the AI features.

## 📋 Table of Contents

1. [Features](#features)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Usage](#usage)
5. [AI Providers](#ai-providers)
6. [Examples](#examples)
7. [Troubleshooting](#troubleshooting)

---

## Features

### ✅ What AI Integration Adds

1. **Natural Conversations**
   - More human-like responses
   - Better understanding of context
   - Conversational memory

2. **Enhanced Customer Experience**
   - Warm, personalized interactions
   - Better handling of complex queries
   - Professional yet friendly tone

3. **Intelligent Responses**
   - Context-aware answers
   - Service recommendations
   - Helpful suggestions

4. **Hybrid Approach**
   - AI for general conversations
   - Structured flow for booking actions
   - Automatic fallback on errors

### 🔄 How It Works

The system uses a **hybrid approach**:

- **AI Mode**: For general inquiries, greetings, and conversations
- **Structured Mode**: For booking actions (booking, rescheduling, cancellation)
- **Automatic Fallback**: Switches to rule-based if AI fails

---

## Installation

### 1. Update Dependencies

```bash
cd massage_booking_agent
pip install -r requirements.txt
```

Required AI packages:
- `openai==1.12.0`
- `anthropic==0.18.0`
- `httpx==0.26.0`

### 2. Configure Environment

Copy and edit `.env` file:

```bash
cp .env.example .env
```

Add your AI credentials:

```env
# AI Provider Configuration
AI_PROVIDER="openai"  # or "grok" or "rule_based"

# OpenAI Configuration
OPENAI_API_KEY="sk-your-openai-api-key-here"
OPENAI_MODEL="gpt-4-turbo-preview"
OPENAI_TEMPERATURE=0.7

# Grok Configuration
GROK_API_KEY="your-grok-api-key-here"
GROK_MODEL="grok-1"
GROK_TEMPERATURE=0.7
```

### 3. Test Installation

```bash
python test_ai_integration.py
```

All tests should pass with green checkmarks.

---

## Configuration

### AI Provider Selection

Set `AI_PROVIDER` in `.env`:

```env
AI_PROVIDER="openai"    # Use OpenAI GPT
AI_PROVIDER="grok"      # Use Grok (xAI)
AI_PROVIDER="rule_based"  # Use rule-based only
```

### Model Configuration

#### OpenAI

```env
OPENAI_MODEL="gpt-4-turbo-preview"  # Options:
# - gpt-4-turbo-preview (best, recommended)
# - gpt-4
# - gpt-3.5-turbo (faster, cheaper)
OPENAI_TEMPERATURE=0.7  # 0.0 (strict) to 1.0 (creative)
```

#### Grok

```env
GROK_MODEL="grok-1"
GROK_TEMPERATURE=0.7
```

---

## Usage

### Starting the Server

```bash
# Start with default provider (from .env)
python api/flask_app.py

# Or override provider
AI_PROVIDER=openai python api/flask_app.py
```

### API Endpoint

Send messages to the agent:

```bash
curl -X POST http://localhost:5000/message \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "5551234567",
    "message": "Hi, I want to book a massage"
  }'
```

---

## Examples

### Example 1: General Inquiry

**Client:** "Hi, how are you today?"

**AI Response:** "Hello! I'm doing great, thank you for asking. I'm here to help you with booking a massage or answer any questions you might have about our services. How can I assist you today?"

### Example 2: Service Information

**Client:** "What services do you offer?"

**AI Response:** "We offer several massage therapies to help you relax and rejuvenate..."

### Example 3: Booking Transition

**Client:** "I'd like to book a Swedish massage"

**System:** Switches to structured flow

**Agent:** "Great choice! What date would you like to schedule your appointment?"

---

## Troubleshooting

### Issue: AI Not Working

**Solutions:**

1. Check API Key is set in `.env`
2. Verify `AI_PROVIDER` is correctly set
3. Run `python test_ai_integration.py`
4. Check logs in `logs/` directory

### Issue: High API Costs

**Solutions:**

1. Use GPT-3.5 for simpler queries
2. Increase temperature for more variability
3. Monitor usage in provider dashboard
4. Use rule-based for common queries

---

## Best Practices

1. **Cost Management** - Monitor API usage, set up alerts
2. **Performance** - Keep conversation history short
3. **Quality** - Test with real user queries
4. **Reliability** - Always have rule-based fallback
5. **Security** - Never commit API keys, rotate regularly

---

## Support

For issues:
1. Check this guide first
2. Review test suite output
3. Check logs for errors
4. Consult provider documentation

**Next Steps:**
1. Set up your AI provider
2. Test with real conversations
3. Monitor usage and costs
4. Fine-tune prompts and settings