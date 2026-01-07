"""
Flask API for the massage booking agent
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.booking_agent import BookingAgent
from agent.ai_booking_agent import AIBookingAgent

app = Flask(__name__)
CORS(app)

# Get AI provider from environment
ai_provider = os.getenv("AI_PROVIDER", "openai").lower()

# Initialize the appropriate agent
try:
    agent = AIBookingAgent(ai_provider)
    print(f"✓ Initialized AI Booking Agent with provider: {ai_provider}")
except Exception as e:
    print(f"⚠ Failed to initialize AI agent: {e}")
    print("ℹ Falling back to standard Booking Agent")
    agent = BookingAgent()


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    ai_status = {
        "enabled": hasattr(agent, 'ai_enabled') and agent.ai_enabled,
        "provider": getattr(agent, 'ai_provider', 'none') if hasattr(agent, 'ai_provider') else 'none'
    }
    
    return jsonify({
        "status": "healthy", 
        "service": "massage_booking_agent",
        "ai": ai_status
    }), 200


@app.route('/message', methods=['POST'])
def handle_message():
    """
    Handle incoming messages from clients
    
    Expected JSON payload:
    {
        "phone_number": "1234567890",
        "message": "I'd like to book a massage"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        phone_number = data.get('phone_number')
        message = data.get('message')
        use_ai = data.get('use_ai', True)  # Allow client to force AI mode
        
        if not phone_number or not message:
            return jsonify({"error": "phone_number and message are required"}), 400
        
        # Process the message
        response = agent.process_message(phone_number, message)
        
        # Get conversation info if AI agent is being used
        conversation_info = None
        if hasattr(agent, 'get_conversation_info'):
            conversation_info = agent.get_conversation_info(phone_number)
        
        return jsonify({
            "success": True,
            "response": response,
            "phone_number": phone_number,
            "conversation": conversation_info
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/availability', methods=['GET'])
def check_availability():
    """
    Check availability for a specific date
    
    Query parameters:
    - date: YYYY-MM-DD format
    """
    try:
        date = request.args.get('date')
        
        if not date:
            # Return available dates
            available_dates = agent.scheduler.get_available_dates(14)
            return jsonify({
                "success": True,
                "available_dates": available_dates
            }), 200
        
        # Return time slots for specific date
        available_slots = agent.scheduler.get_available_slots(date)
        
        return jsonify({
            "success": True,
            "date": date,
            "available_slots": available_slots
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/services', methods=['GET'])
def get_services():
    """Get list of available services"""
    try:
        services = agent.scheduler.get_all_services()
        return jsonify({
            "success": True,
            "services": services
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/appointments/<phone_number>', methods=['GET'])
def get_client_appointments(phone_number):
    """Get appointments for a client"""
    try:
        appointments = agent.appointment_manager.get_client_appointments(phone_number)
        
        appointments_data = []
        for appt in appointments:
            appointments_data.append({
                "id": appt.id,
                "service": appt.service,
                "date": appt.date,
                "time": appt.time,
                "duration": appt.duration,
                "price": appt.price,
                "status": appt.status,
                "payment_status": appt.payment_status
            })
        
        return jsonify({
            "success": True,
            "appointments": appointments_data
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/appointments/<appointment_id>/cancel', methods=['POST'])
def cancel_appointment(appointment_id):
    """Cancel an appointment"""
    try:
        success = agent.appointment_manager.cancel_appointment(appointment_id)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Appointment cancelled successfully"
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Appointment not found"
            }), 404
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    """
    Handle Stripe webhook events
    """
    try:
        import stripe
        import json
        
        payload = request.data
        sig_header = request.headers.get('Stripe-Signature')
        
        # In production, verify webhook signature
        # event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        
        event = json.loads(payload)
        
        if event['type'] == 'payment_intent.succeeded':
            payment_intent_id = event['data']['object']['id']
            
            # Notify client and update appointment
            client_phone = agent.handle_payment_webhook(payment_intent_id)
            
            if client_phone:
                # Send confirmation to client
                state = agent._get_conversation_state(client_phone)
                state["stage"] = "confirmed"
        
        return jsonify({"success": True}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/clients/<phone_number>', methods=['GET'])
def get_client_info(phone_number):
    """Get client information"""
    try:
        client = agent.client_manager.get_client_by_phone(phone_number)
        
        if client:
            return jsonify({
                "success": True,
                "client": client.to_dict()
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Client not found"
            }), 404
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/admin/upcoming', methods=['GET'])
def get_upcoming_appointments():
    """Get all upcoming appointments (admin endpoint)"""
    try:
        upcoming = agent.appointment_manager.get_upcoming_appointments()
        
        appointments_data = []
        for appt in upcoming:
            client = agent.client_manager.get_client_by_phone(appt.client_phone)
            appointments_data.append({
                "id": appt.id,
                "client_name": client.name if client else "Unknown",
                "client_phone": appt.client_phone,
                "service": appt.service,
                "date": appt.date,
                "time": appt.time,
                "status": appt.status,
                "payment_status": appt.payment_status
            })
        
        return jsonify({
            "success": True,
            "appointments": appointments_data
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # Test AI connection if enabled
    if hasattr(agent, 'ai_enabled') and agent.ai_enabled:
        try:
            ai_working = agent.ai_agent.test_ai_connection()
            if ai_working:
                print(f"✓ AI service ({ai_provider}) is working!")
            else:
                print(f"⚠ AI service ({ai_provider}) connection failed")
        except Exception as e:
            print(f"⚠ AI service test error: {e}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)