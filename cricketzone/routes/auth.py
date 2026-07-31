"""
cricketzone/routes/auth.py — Signup, Login, Logout, Email Verification
"""

from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from cricketzone.models import (
    create_user, get_user_by_email, get_user_by_token,
    mark_user_verified, set_verification_token
)
from cricketzone.utils.auth import (
    generate_verification_token, token_created_at_now, is_token_expired
)
from cricketzone.utils.email import send_verification_email

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if session.get("user_id"):
        return redirect(url_for("main.index"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email     = request.form.get("email", "").strip().lower()
        phone     = request.form.get("phone", "").strip()
        password  = request.form.get("password", "")
        confirm   = request.form.get("confirm_password", "")

        errors = []
        if not full_name:
            errors.append("Full name is required.")
        if not email:
            errors.append("Email address is required.")
        if len(password) < 6:
            errors.append("Password must be at least 6 characters long.")
        if password != confirm:
            errors.append("Passwords do not match.")
        if email and get_user_by_email(email):
            errors.append("An account with this email already exists. Please login instead.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("auth/signup.html", form_data=request.form)

        token = generate_verification_token()
        create_user({
            "full_name":          full_name,
            "email":              email,
            "phone":              phone,
            "password_hash":      generate_password_hash(password),
            "verification_token": token,
            "token_created_at":   token_created_at_now(),
        })

        verification_url = url_for("auth.verify_email", token=token, _external=True)
        email_sent = send_verification_email(
            {"full_name": full_name, "email": email}, verification_url
        )

        if email_sent:
            flash("Account created! Please check your email to verify your account before logging in.", "success")
        else:
            flash(
                "Account created, but the verification email could not be sent. "
                "Please try 'Resend verification email' from the login page.",
                "warning"
            )

        return redirect(url_for("auth.login"))

    return render_template("auth/signup.html", form_data={})


@auth_bp.route("/verify-email/<token>")
def verify_email(token):
    user = get_user_by_token(token)

    if not user:
        flash("This verification link is invalid or has already been used.", "danger")
        return redirect(url_for("auth.login"))

    if is_token_expired(user["token_created_at"]):
        flash("This verification link has expired. Please request a new one below.", "danger")
        return redirect(url_for("auth.resend_verification", email=user["email"]))

    mark_user_verified(user["id"])
    flash("Your email has been verified! You can now login.", "success")
    return redirect(url_for("auth.login"))


@auth_bp.route("/resend-verification", methods=["GET", "POST"])
def resend_verification():
    prefill_email = request.args.get("email", "")

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        user = get_user_by_email(email)

        if not user:
            flash("No account found with that email address.", "danger")
        elif user["is_verified"]:
            flash("This account is already verified. Please login.", "info")
            return redirect(url_for("auth.login"))
        else:
            token = generate_verification_token()
            set_verification_token(user["id"], token, token_created_at_now())
            verification_url = url_for("auth.verify_email", token=token, _external=True)
            send_verification_email(
                {"full_name": user["full_name"], "email": user["email"]}, verification_url
            )
            flash("A new verification email has been sent — please check your inbox.", "success")
            return redirect(url_for("auth.login"))

    return render_template("auth/resend_verification.html", prefill_email=prefill_email)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("main.index"))

    next_url = request.values.get("next") or url_for("main.index")

    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        next_url = request.form.get("next") or next_url

        user = get_user_by_email(email)

        if not user or not check_password_hash(user["password_hash"], password):
            flash("Invalid email or password.", "danger")
            return render_template("auth/login.html", next=next_url)

        if not user["is_verified"]:
            flash("Please verify your email before logging in. Check your inbox for the verification link.", "warning")
            return render_template("auth/login.html", next=next_url, unverified_email=user["email"])

        session.clear()
        session["user_id"]   = user["id"]
        session["user_name"] = user["full_name"]
        flash(f"Welcome back, {user['full_name']}!", "success")
        return redirect(next_url)

    return render_template("auth/login.html", next=next_url)


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))