"""
Payment processing module for handling deposits and payments
"""
import stripe
from typing import Optional, Tuple
from config.settings import (
    STRIPE_SECRET_KEY, DEPOSIT_ENABLED, DEPOSIT_REQUEST,
    BUSINESS_NAME
)


class PaymentProcessor:
    """Handles payment processing using Stripe"""
    
    def __init__(self):
        if STRIPE_SECRET_KEY:
            stripe.api_key = STRIPE_SECRET_KEY
        else:
            print("Warning: Stripe secret key not configured")

    def create_payment_link(self, amount: float, appointment_id: str, 
                          client_email: Optional[str] = None) -> Tuple[str, str]:
        """
        Create a Stripe payment link for deposit
        
        Returns:
            Tuple of (payment_url, payment_intent_id)
        """
        if not STRIPE_SECRET_KEY:
            raise Exception("Stripe is not configured. Please set STRIPE_SECRET_KEY.")
        
        try:
            # Create product for the deposit
            product = stripe.Product.create(
                name=f"Deposit for {BUSINESS_NAME}",
                description=f"Deposit for appointment {appointment_id[:8]}..."
            )
            
            # Create price
            price = stripe.Price.create(
                product=product.id,
                unit_amount=int(amount * 100),  # Convert to cents
                currency="usd"
            )
            
            # Create payment link
            payment_link = stripe.PaymentLink.create(
                price=price.id,
                allow_promotion_codes=True,
                billing_address_collection="auto",
                after_completion={
                    "type": "redirect",
                    "redirect": {
                        "url": f"https://your-website.com/confirmation?appointment_id={appointment_id}"
                    }
                }
            )
            
            return payment_link.url, payment_link.payment_intent
            
        except stripe.error.StripeError as e:
            print(f"Stripe error: {e}")
            raise Exception(f"Payment processing error: {str(e)}")

    def create_checkout_session(self, amount: float, appointment_id: str,
                                success_url: str, cancel_url: str,
                                client_email: Optional[str] = None) -> Tuple[str, str]:
        """
        Create a Stripe checkout session
        
        Returns:
            Tuple of (checkout_url, payment_intent_id)
        """
        if not STRIPE_SECRET_KEY:
            raise Exception("Stripe is not configured. Please set STRIPE_SECRET_KEY.")
        
        try:
            checkout_params = {
                "payment_method_types": ["card"],
                "line_items": [{
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": f"Deposit for {BUSINESS_NAME}",
                            "description": f"Appointment ID: {appointment_id[:8]}...",
                        },
                        "unit_amount": int(amount * 100),
                    },
                    "quantity": 1,
                }],
                "mode": "payment",
                "success_url": success_url,
                "cancel_url": cancel_url,
            }
            
            if client_email:
                checkout_params["customer_email"] = client_email
            
            session = stripe.checkout.Session.create(**checkout_params)
            
            return session.url, session.payment_intent
            
        except stripe.error.StripeError as e:
            print(f"Stripe error: {e}")
            raise Exception(f"Payment processing error: {str(e)}")

    def verify_payment(self, payment_intent_id: str) -> Tuple[bool, float]:
        """
        Verify if a payment was successful
        
        Returns:
            Tuple of (is_successful, amount)
        """
        if not STRIPE_SECRET_KEY:
            return False, 0.0
        
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            if payment_intent.status == "succeeded":
                amount = payment_intent.amount / 100  # Convert from cents
                return True, amount
            
            return False, 0.0
            
        except stripe.error.StripeError as e:
            print(f"Stripe error: {e}")
            return False, 0.0

    def create_refund(self, payment_intent_id: str, amount: Optional[float] = None) -> bool:
        """
        Process a refund for a payment
        
        Args:
            payment_intent_id: The payment intent to refund
            amount: Amount to refund (None for full refund)
        
        Returns:
            True if refund was successful
        """
        if not STRIPE_SECRET_KEY:
            return False
        
        try:
            refund_params = {"payment_intent": payment_intent_id}
            
            if amount:
                refund_params["amount"] = int(amount * 100)
            
            stripe.Refund.create(**refund_params)
            return True
            
        except stripe.error.StripeError as e:
            print(f"Stripe error: {e}")
            return False

    def handle_deposit_requirement(self, service: str, price: float, 
                                   appointment_id: str, client_email: Optional[str] = None) -> dict:
        """
        Handle the deposit requirement process
        
        Returns:
            Dictionary with deposit information
        """
        from config.settings import (
            DEPOSIT_ENABLED, DEPOSIT_REQUIRED_FOR_SERVICES, DEPOSIT_REQUEST
        )
        
        if not DEPOSIT_ENABLED:
            return {
                "required": False,
                "amount": 0.0,
                "message": "No deposit required for this appointment."
            }
        
        if service not in DEPOSIT_REQUIRED_FOR_SERVICES:
            return {
                "required": False,
                "amount": 0.0,
                "message": "No deposit required for this service."
            }
        
        # Calculate deposit amount
        from core.scheduler import Scheduler
        scheduler = Scheduler(None)
        deposit_amount = scheduler.calculate_deposit(service, price)
        
        if deposit_amount <= 0:
            return {
                "required": False,
                "amount": 0.0,
                "message": "No deposit required for this appointment."
            }
        
        # Create payment link
        try:
            payment_url, payment_intent_id = self.create_payment_link(
                deposit_amount, appointment_id, client_email
            )
            
            return {
                "required": True,
                "amount": deposit_amount,
                "payment_url": payment_url,
                "payment_intent_id": payment_intent_id,
                "message": DEPOSIT_REQUEST.format(
                    deposit_amount=deposit_amount,
                    payment_link=payment_url
                )
            }
            
        except Exception as e:
            return {
                "required": True,
                "amount": deposit_amount,
                "error": str(e),
                "message": f"Error creating payment link: {str(e)}"
            }

    def check_deposit_status(self, payment_intent_id: str) -> Tuple[bool, float]:
        """
        Check the status of a deposit payment
        
        Returns:
            Tuple of (is_paid, amount)
        """
        return self.verify_payment(payment_intent_id)