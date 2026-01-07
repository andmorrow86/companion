"""
Demo script to showcase the booking agent functionality
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.booking_agent import BookingAgent
from datetime import datetime, timedelta


def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def print_agent_response(response):
    """Print agent response with formatting"""
    print(f"🤖 Agent: {response}\n")


def print_client_message(message):
    """Print client message with formatting"""
    print(f"👤 Client: {message}")


def simulate_conversation(agent, phone_number, messages):
    """Simulate a conversation with the agent"""
    print_header("Booking Conversation Simulation")
    
    for message in messages:
        print_client_message(message)
        response = agent.process_message(phone_number, message)
        print_agent_response(response)
        
        # Add delay for realism
        import time
        time.sleep(1)


def demo_basic_booking():
    """Demo basic booking flow"""
    agent = BookingAgent()
    phone_number = "5551234567"
    
    messages = [
        "Hi, I'd like to book a massage",
        "What services do you offer?",
        "I'd like a deep tissue massage",
        "Tomorrow",
        "What time is available?",
        "2pm works for me"
    ]
    
    simulate_conversation(agent, phone_number, messages)


def demo_with_deposit():
    """Demo booking with deposit requirement"""
    agent = BookingAgent()
    phone_number = "5559876543"
    
    print_header("Booking with Deposit Demo")
    
    messages = [
        "I want to book a hot stone massage",
        "Next Monday at 3pm"
    ]
    
    simulate_conversation(agent, phone_number, messages)


def demo_check_availability():
    """Demo availability checking"""
    agent = BookingAgent()
    
    print_header("Availability Checking Demo")
    
    # Check available dates
    print("Checking available dates for next 2 weeks...")
    available_dates = agent.scheduler.get_available_dates(14)
    
    if available_dates:
        print(f"✓ Found {len(available_dates)} available dates:")
        for date in available_dates[:5]:
            print(f"  - {agent.scheduler.format_date_display(date)}")
        
        # Check slots for first available date
        first_date = available_dates[0]
        print(f"\nChecking time slots for {agent.scheduler.format_date_display(first_date)}...")
        slots = agent.scheduler.get_available_slots(first_date)
        
        if slots:
            print(f"✓ Available slots:")
            for slot in slots[:8]:
                print(f"  - {agent.scheduler.format_time_display(slot)}")
        else:
            print("✗ No slots available")
    else:
        print("✗ No available dates found")


def demo_services_info():
    """Demo services information"""
    agent = BookingAgent()
    
    print_header("Services Information Demo")
    
    services = agent.scheduler.get_all_services()
    print("Available Services:")
    print("-" * 70)
    
    for key, info in services.items():
        print(f"• {info['name']}")
        print(f"  Duration: {info['duration']} minutes")
        print(f"  Price: ${info['price']}")
        
        # Calculate deposit
        deposit = agent.scheduler.calculate_deposit(key, info['price'])
        if deposit > 0:
            print(f"  Deposit Required: ${deposit}")
        print()


def demo_cancellation():
    """Demo cancellation process"""
    agent = BookingAgent()
    phone_number = "5551112222"
    
    print_header("Cancellation Demo")
    
    # First create a booking
    print("Creating a test booking...")
    agent.process_message(phone_number, "I want to book a Swedish massage tomorrow at 10am")
    
    # Now cancel it
    messages = [
        "I need to cancel my appointment",
        "Yes, please cancel it"
    ]
    
    simulate_conversation(agent, phone_number, messages)


def demo_reschedule():
    """Demo rescheduling process"""
    agent = BookingAgent()
    phone_number = "5553334444"
    
    print_header("Rescheduling Demo")
    
    # First create a booking
    print("Creating a test booking...")
    agent.process_message(phone_number, "Book a Swedish massage for Friday at 2pm")
    
    # Now reschedule it
    messages = [
        "I need to reschedule my appointment",
        "I'd like to move it to Saturday at 11am"
    ]
    
    simulate_conversation(agent, phone_number, messages)


def demo_nlp_capabilities():
    """Demo natural language understanding"""
    from core.nlu import NLU
    
    print_header("Natural Language Understanding Demo")
    
    nlu = NLU()
    
    test_messages = [
        "I want to book a deep tissue massage for tomorrow at 3pm",
        "Can I schedule a hot stone treatment next Monday morning?",
        "I need to cancel my appointment on Friday",
        "What services do you offer?",
        "How much is a couples massage?",
        "Are you open on Sundays?",
        "I'd like to reschedule to next week",
    ]
    
    print("Message Analysis:")
    print("-" * 70)
    
    for msg in test_messages:
        intent, data = nlu.parse_booking_request(msg)
        print(f"Message: {msg}")
        print(f"Intent: {intent}")
        print(f"Extracted Service: {data.get('service') or 'None'}")
        print(f"Extracted Date: {data.get('date') or 'None'}")
        print(f"Extracted Time: {data.get('time') or 'None'}")
        print()


def interactive_demo():
    """Interactive demo where user can chat with the agent"""
    agent = BookingAgent()
    
    print_header("Interactive Demo")
    print("Chat with the booking agent! Type 'quit' to exit.\n")
    
    phone_number = input("Enter your phone number (or press Enter for default): ").strip()
    if not phone_number:
        phone_number = "5555555555"
    
    print(f"\n📞 Using phone number: {phone_number}")
    print("Type your message and press Enter to send.\n")
    
    while True:
        try:
            user_input = input("👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\n👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            response = agent.process_message(phone_number, user_input)
            print(f"\n🤖 Agent: {response}\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


def main():
    """Main demo menu"""
    print("\n" + "="*70)
    print("  MASSAGE PARLOR BOOKING AGENT - DEMO")
    print("="*70)
    
    demos = {
        "1": ("Basic Booking Flow", demo_basic_booking),
        "2": ("Booking with Deposit", demo_with_deposit),
        "3": ("Check Availability", demo_check_availability),
        "4": ("Services Information", demo_services_info),
        "5": ("Cancellation Process", demo_cancellation),
        "6": ("Rescheduling Process", demo_reschedule),
        "7": ("NLP Capabilities", demo_nlp_capabilities),
        "8": ("Interactive Chat", interactive_demo),
    }
    
    print("\nAvailable Demos:")
    for key, (name, _) in demos.items():
        print(f"  {key}. {name}")
    print("  0. Exit")
    
    while True:
        choice = input("\nSelect a demo (0-8): ").strip()
        
        if choice == "0":
            print("\n👋 Thank you for exploring the Massage Parlor Booking Agent!")
            break
        
        if choice in demos:
            name, func = demos[choice]
            try:
                func()
            except Exception as e:
                print(f"\n❌ Error running demo: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("❌ Invalid choice. Please select 0-8.")


if __name__ == "__main__":
    main()