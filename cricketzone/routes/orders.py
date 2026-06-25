"""
cricketzone/routes/orders.py — Purchase, Success, Tracking
"""

import datetime
import pytz
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from cricketzone.models import (
    get_product_by_id, get_stock, create_order,
    get_order_by_order_id, get_order_tracking,
    get_all_products
)
from cricketzone.utils import generate_order_id, send_order_email

orders_bp = Blueprint("orders", __name__)
IST = pytz.timezone("Asia/Kolkata")


@orders_bp.route("/purchase/<int:product_id>", methods=["GET", "POST"])
def purchase(product_id):
    product = get_product_by_id(product_id)
    if not product:
        abort(404)

    if request.method == "POST":
        name    = request.form.get("name",    "").strip()
        email   = request.form.get("email",   "").strip()
        phone   = request.form.get("phone",   "").strip()
        address = request.form.get("address", "").strip()
        qty_str = request.form.get("quantity","1").strip()

        errors = []
        if not name:    errors.append("Full name is required.")
        if not email:   errors.append("Email address is required.")
        if not address: errors.append("Delivery address is required.")
        try:
            qty = int(qty_str)
            if qty < 1: raise ValueError
        except ValueError:
            errors.append("Quantity must be a positive whole number.")
            qty = 1

        if errors:
            for e in errors: flash(e, "danger")
            return render_template("orders/purchase.html", product=product)

        current_stock = get_stock(product_id)
        if current_stock < qty:
            flash(f"Only {current_stock} unit(s) in stock. Please reduce quantity.", "warning")
            return render_template("orders/purchase.html", product=product)

        order_id    = generate_order_id()
        total_price = round(product["price"] * qty, 2)

        # IST time
        ist_now = datetime.datetime.now(IST)
        created_at_display = ist_now.strftime("%d %b %Y, %I:%M %p IST")

        order_data = {
            "order_id":           order_id,
            "customer_name":      name,
            "customer_email":     email,
            "customer_phone":     phone,
            "product_id":         product_id,
            "quantity":           qty,
            "total_price":        total_price,
            "address":            address,
            "status":             "Confirmed",
            "created_at_display": created_at_display,
        }
        create_order(order_data)
        send_order_email(order_data, dict(product))

        flash(f"Order {order_id} placed! Confirmation email sent.", "success")
        return redirect(url_for("orders.order_success", order_id=order_id))

    return render_template("orders/purchase.html", product=product)


@orders_bp.route("/order/success/<order_id>")
def order_success(order_id):
    order = get_order_by_order_id(order_id)
    if not order: abort(404)
    return render_template("orders/order_success.html", order=order)


@orders_bp.route("/track", methods=["GET", "POST"])
def track_order():
    order = None
    if request.method == "POST":
        oid = request.form.get("order_id", "").strip().upper()
        if oid:
            order = get_order_tracking(oid)
            if not order:
                flash("No order found with that ID. Please check and try again.", "warning")
    return render_template("orders/order_tracking.html", order=order)