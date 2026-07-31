"""
cricketzone/routes/orders.py — Purchase, Success, Tracking, Razorpay Payment
"""

import datetime
import pytz
from flask import (
    Blueprint, render_template, request, redirect, url_for,
    flash, abort, jsonify, current_app
)
from cricketzone.models import (
    get_product_by_id, get_stock, create_order,
    get_order_by_order_id, get_order_tracking,
    get_all_products
)
from cricketzone.utils import generate_order_id, send_order_email
from cricketzone.utils.payment import create_razorpay_order, verify_payment_signature
from cricketzone.utils.auth import login_required, current_user

orders_bp = Blueprint("orders", __name__)
IST = pytz.timezone("Asia/Kolkata")


@orders_bp.route("/purchase/<int:product_id>", methods=["GET", "POST"])
@login_required
def purchase(product_id):
    product = get_product_by_id(product_id)
    if not product:
        abort(404)

    user = current_user()

    if request.method == "POST":
        name    = user["full_name"]
        email   = user["email"]
        phone   = request.form.get("phone", "").strip() or (user["phone"] or "")
        address = request.form.get("address", "").strip()
        qty_str = request.form.get("quantity", "1").strip()

        errors = []
        if not address: errors.append("Delivery address is required.")
        try:
            qty = int(qty_str)
            if qty < 1: raise ValueError
        except ValueError:
            errors.append("Quantity must be a positive whole number.")
            qty = 1

        if errors:
            for e in errors: flash(e, "danger")
            return render_template("orders/purchase.html", product=product, user=user)

        current_stock = get_stock(product_id)
        if current_stock < qty:
            flash(f"Only {current_stock} unit(s) in stock. Please reduce quantity.", "warning")
            return render_template("orders/purchase.html", product=product, user=user)

        razorpay_order_id   = request.form.get("razorpay_order_id", "").strip()
        razorpay_payment_id = request.form.get("razorpay_payment_id", "").strip()
        razorpay_signature  = request.form.get("razorpay_signature", "").strip()

        if not (razorpay_order_id and razorpay_payment_id and razorpay_signature):
            flash("Payment was not completed. Please click 'Place Order' and finish the payment to confirm your order.", "danger")
            return render_template("orders/purchase.html", product=product, user=user)

        if not verify_payment_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature):
            flash("Payment verification failed. If any amount was deducted, please contact us with your payment ID.", "danger")
            return render_template("orders/purchase.html", product=product, user=user)

        order_id    = generate_order_id()
        total_price = round(product["price"] * qty, 2)

        ist_now = datetime.datetime.now(IST)
        created_at_display = ist_now.strftime("%d %b %Y, %I:%M %p IST")

        order_data = {
            "order_id":             order_id,
            "customer_name":        name,
            "customer_email":       email,
            "customer_phone":       phone,
            "product_id":           product_id,
            "quantity":             qty,
            "total_price":          total_price,
            "address":              address,
            "status":               "Confirmed",
            "created_at_display":   created_at_display,
            "razorpay_order_id":    razorpay_order_id,
            "razorpay_payment_id":  razorpay_payment_id,
            "payment_status":       "Paid",
            "user_id":              user["id"],
        }
        create_order(order_data)
        email_sent = send_order_email(order_data, dict(product))

        if email_sent:
            flash(f"Payment successful! Order {order_id} placed and confirmation email sent.", "success")
        else:
            flash(f"Payment successful! Order {order_id} placed. (Confirmation email could not be sent — please save your Order ID: {order_id})", "warning")

        return redirect(url_for("orders.order_success", order_id=order_id))

    return render_template("orders/purchase.html", product=product, user=user)


@orders_bp.route("/purchase/<int:product_id>/create-payment-order", methods=["POST"])
@login_required
def create_payment_order(product_id):
    product = get_product_by_id(product_id)
    if not product:
        return jsonify({"error": "Product not found."}), 404

    qty_str = request.form.get("quantity", "1").strip()
    try:
        qty = int(qty_str)
        if qty < 1:
            raise ValueError
    except ValueError:
        return jsonify({"error": "Invalid quantity."}), 400

    current_stock = get_stock(product_id)
    if current_stock < qty:
        return jsonify({"error": f"Only {current_stock} unit(s) in stock."}), 400

    amount = round(product["price"] * qty, 2)
    receipt = f"CZ-{product_id}-{int(datetime.datetime.now().timestamp())}"

    try:
        razorpay_order = create_razorpay_order(amount_rupees=amount, receipt=receipt)
    except Exception as exc:
        current_app.logger.error("Razorpay order creation failed: %s", exc)
        return jsonify({"error": "Payment gateway error. Please try again in a moment."}), 500

    user = current_user()
    return jsonify({
        "razorpay_order_id": razorpay_order["id"],
        "amount":            razorpay_order["amount"],
        "currency":          razorpay_order["currency"],
        "key":               current_app.config["RAZORPAY_KEY_ID"],
        "product_name":      product["name"],
        "customer_name":     user["full_name"],
        "customer_email":    user["email"],
        "customer_phone":    user["phone"] or "",
    })


@orders_bp.route("/order/success/<order_id>")
@login_required
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