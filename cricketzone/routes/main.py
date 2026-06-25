"""
cricketzone/routes/main.py — Home & Search
"""

import datetime
import pytz
from flask import Blueprint, render_template, request
from cricketzone.models import get_featured_products, search_products, get_counts

main_bp = Blueprint("main", __name__)

IST = pytz.timezone("Asia/Kolkata")


def get_ist_now():
    return datetime.datetime.now(IST)


@main_bp.context_processor
def inject_globals():
    return {"current_year": get_ist_now().year}


@main_bp.route("/")
def index():
    counts = get_counts()
    return render_template(
        "index.html",
        featured_bats  = get_featured_products("bat",  4),
        featured_balls = get_featured_products("ball", 4),
        featured_kits  = get_featured_products("kit",  4),
        total_products = counts["products"],
        total_orders   = counts["orders"],
    )


@main_bp.route("/search")
def search():
    q       = request.args.get("q", "").strip()
    results = search_products(q) if q else []
    return render_template("search.html", results=results, query=q)