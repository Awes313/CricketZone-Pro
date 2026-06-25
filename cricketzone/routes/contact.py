"""
cricketzone/routes/contact.py — Contact Form
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from cricketzone.models import create_message

contact_bp = Blueprint("contact", __name__)


@contact_bp.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name    = request.form.get("name",    "").strip()
        email   = request.form.get("email",   "").strip()
        subject = request.form.get("subject", "").strip()
        message = request.form.get("message", "").strip()

        if not name or not email or not message:
            flash("Name, email, and message are all required.", "danger")
            return render_template("contact.html")

        create_message(name, email, subject, message)
        flash("Message received! We will get back to you within 24 hours.", "success")
        return redirect(url_for("contact.contact"))

    return render_template("contact.html")