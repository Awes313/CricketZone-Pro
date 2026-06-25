"""
cricketzone/utils/email.py — Email Helper
Gmail ke liye App Password use karo (not regular password).
"""

import logging
from flask import render_template
from cricketzone import mail

logger = logging.getLogger(__name__)


def send_order_email(order: dict, product: dict) -> bool:
    from flask_mail import Message
    try:
        msg = Message(
            subject=f"Order Confirmed – {order['order_id']} | CricketZone",
            recipients=[order["customer_email"]],
            sender=("CricketZone", "mohammed7777awes@gmail.com"),
        )
        msg.html = render_template(
            "orders/email_confirmation.html",
            order=order,
            product=product,
        )
        mail.send(msg)
        logger.info("Email sent for order %s", order["order_id"])
        return True
    except Exception as exc:
        logger.warning("Email failed for %s: %s", order.get("order_id"), exc)
        print(f"EMAIL ERROR: {exc}")
        return False