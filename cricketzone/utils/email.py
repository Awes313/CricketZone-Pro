"""
cricketzone/utils/email.py — Email Helper
Gmail ke liye App Password use karo (not regular password).
"""

import logging
from flask import render_template, current_app
from cricketzone import mail

logger = logging.getLogger(__name__)


def send_order_email(order: dict, product: dict) -> bool:
    from flask_mail import Message
    try:
        sender_email = current_app.config["MAIL_USERNAME"]
        msg = Message(
            subject=f"Order Confirmed – {order['order_id']} | CricketZone",
            recipients=[order["customer_email"]],
            sender=("CricketZone", sender_email),
        )
        msg.html = render_template(
            "orders/email_confirmation.html",
            order=order,
            product=product,
        )
        
        print("MAIL_USERNAME:", current_app.config["MAIL_USERNAME"])
        print("MAIL_SERVER:", current_app.config["MAIL_SERVER"])
        print("MAIL_PORT:", current_app.config["MAIL_PORT"])
        print("MAIL_TLS:", current_app.config["MAIL_USE_TLS"])

        mail.send(msg)
        logger.info("Email sent for order %s", order["order_id"])
        return True
    except Exception as exc:
        logger.warning("Email failed for %s: %s", order.get("order_id"), exc)
        print(f"EMAIL ERROR: {exc}")
        return False


def send_verification_email(user: dict, verification_url: str) -> bool:
    from flask_mail import Message
    try:
        sender_email = current_app.config["MAIL_USERNAME"]
        msg = Message(
            subject="Verify your CricketZone account",
            recipients=[user["email"]],
            sender=("CricketZone", sender_email),
        )
        msg.html = render_template(
            "auth/verification_email.html",
            full_name=user["full_name"],
            verification_url=verification_url,
        )
        mail.send(msg)
        logger.info("Verification email sent to %s", user["email"])
        return True
    except Exception as exc:
        logger.warning("Verification email failed for %s: %s", user.get("email"), exc)
        print(f"EMAIL ERROR: {exc}")
        return False