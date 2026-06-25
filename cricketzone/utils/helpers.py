"""
cricketzone/utils/helpers.py — Utility Functions
"""

import csv
import datetime
from io import StringIO
from functools import wraps

from flask import session, redirect, url_for, flash, make_response
from cricketzone.database import query_db


def generate_order_id():
    year = datetime.datetime.now().year
    last = query_db("SELECT order_id FROM orders ORDER BY id DESC LIMIT 1", one=True)
    if last:
        try:
            new_num = int(last["order_id"].split("-")[-1]) + 1
        except (ValueError, IndexError):
            new_num = 1001
    else:
        new_num = 1001
    return f"CZ-{year}-{new_num}"


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_logged_in"):
            flash("Please log in to access the admin panel.", "warning")
            return redirect(url_for("admin.login"))
        return f(*args, **kwargs)
    return decorated


def csv_response(filename, headers, rows):
    si = StringIO()
    w  = csv.writer(si)
    w.writerow(headers)
    for row in rows:
        w.writerow([row[h] for h in headers])
    out = make_response(si.getvalue())
    out.headers["Content-Disposition"] = f"attachment; filename={filename}"
    out.headers["Content-Type"]        = "text/csv"
    return out