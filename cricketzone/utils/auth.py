"""
cricketzone/utils/auth.py — Session-based login helpers + verification tokens
"""

import secrets
import datetime
from functools import wraps

from flask import session, redirect, url_for, flash, request

from cricketzone.models import get_user_by_id

TOKEN_EXPIRY_HOURS = 24


def generate_verification_token():
    """Cryptographically secure random token for the email verification link."""
    return secrets.token_urlsafe(32)


def token_created_at_now():
    """ISO timestamp string used to check token expiry later."""
    return datetime.datetime.utcnow().isoformat()


def is_token_expired(token_created_at_str):
    if not token_created_at_str:
        return True
    try:
        created = datetime.datetime.fromisoformat(token_created_at_str)
    except ValueError:
        return True
    return (datetime.datetime.utcnow() - created) > datetime.timedelta(hours=TOKEN_EXPIRY_HOURS)


def current_user():
    """Returns the logged-in user's DB row, or None if not logged in."""
    user_id = session.get("user_id")
    if not user_id:
        return None
    return get_user_by_id(user_id)


def login_required(view):
    """Route decorator — redirects to login (with ?next=) if not authenticated."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please login to continue.", "warning")
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)
    return wrapped