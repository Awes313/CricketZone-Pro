"""
cricketzone/utils/payment.py — Razorpay Integration

Same pattern as SmartCare X's payment_service.py:
  - create_razorpay_order()   → creates an order on Razorpay before checkout opens
  - verify_payment_signature() → verifies the payment after checkout succeeds
"""

from decimal import Decimal

import razorpay
from flask import current_app


def _client():
    return razorpay.Client(
        auth=(current_app.config["RAZORPAY_KEY_ID"], current_app.config["RAZORPAY_KEY_SECRET"])
    )


def create_razorpay_order(amount_rupees, receipt):
    """Create a Razorpay order. amount_rupees is converted to paise (x100)."""
    amount_paise = int(Decimal(str(amount_rupees)) * 100)
    return _client().order.create(
        {
            "amount": amount_paise,
            "currency": current_app.config.get("RAZORPAY_CURRENCY", "INR"),
            "receipt": receipt,
            "payment_capture": 1,
        }
    )


def verify_payment_signature(order_id, payment_id, signature):
    """Verify the Razorpay payment signature after checkout completes."""
    try:
        _client().utility.verify_payment_signature(
            {
                "razorpay_order_id": order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature,
            }
        )
        return True
    except razorpay.errors.SignatureVerificationError:
        return False
