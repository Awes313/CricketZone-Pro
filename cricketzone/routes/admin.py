"""
cricketzone/routes/admin.py — Admin Panel (Blueprint)
"""

import datetime
from flask import (Blueprint, render_template, request,
                   redirect, url_for, flash, session, current_app)
from cricketzone.models import (
    get_all_products, get_product_by_id, create_product,
    update_product, delete_product, get_all_orders,
    get_recent_orders, update_order_status, get_all_messages,
    delete_message, get_counts, get_low_stock_products,
    get_best_sellers, get_revenue_by_category,
    get_orders_trend, log_action,
)
from cricketzone.utils import admin_required, csv_response

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# ── Auth 

@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("admin_logged_in"):
        return redirect(url_for("admin.dashboard"))
    if request.method == "POST":
        if (request.form.get("username") == current_app.config["ADMIN_USERNAME"] and
                request.form.get("password") == current_app.config["ADMIN_PASSWORD"]):
            session["admin_logged_in"] = True
            log_action("ADMIN_LOGIN", str(datetime.datetime.now()))
            flash("Welcome back, Admin!", "success")
            return redirect(url_for("admin.dashboard"))
        flash("Invalid username or password.", "danger")
    return render_template("admin/admin_login.html")


@admin_bp.route("/logout")
def logout():
    session.pop("admin_logged_in", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("admin.login"))


# ── Dashboard 

@admin_bp.route("/")
@admin_required
def dashboard():
    counts = get_counts()
    return render_template("admin/admin_dashboard.html",
        total_products   = counts["products"],
        total_orders     = counts["orders"],
        total_messages   = counts["messages"],
        total_revenue    = counts["revenue"],
        low_stock        = get_low_stock_products(),
        recent_orders    = get_recent_orders(10),
        best_sellers     = get_best_sellers(5),
        category_revenue = get_revenue_by_category(),
        orders_trend     = get_orders_trend(7),
    )


# ── Products CRUD 

@admin_bp.route("/products")
@admin_required
def products():
    return render_template("admin/admin_products.html", products=get_all_products())


@admin_bp.route("/product/add", methods=["GET", "POST"])
@admin_required
def add_product():
    if request.method == "POST":
        data = _collect_form()
        if data is None:
            return render_template("admin/admin_product_form.html", product=None, action="Add")
        create_product(data)
        log_action("ADD_PRODUCT", f"Added: {data['name']}")
        flash(f"Product '{data['name']}' added successfully.", "success")
        return redirect(url_for("admin.products"))
    return render_template("admin/admin_product_form.html", product=None, action="Add")


@admin_bp.route("/product/edit/<int:product_id>", methods=["GET", "POST"])
@admin_required
def edit_product(product_id):
    product = get_product_by_id(product_id)
    if not product:
        flash("Product not found.", "danger")
        return redirect(url_for("admin.products"))
    if request.method == "POST":
        data = _collect_form()
        if data is None:
            return render_template("admin/admin_product_form.html", product=product, action="Edit")
        update_product(product_id, data)
        log_action("EDIT_PRODUCT", f"Edited ID {product_id}")
        flash("Product updated successfully.", "success")
        return redirect(url_for("admin.products"))
    return render_template("admin/admin_product_form.html", product=product, action="Edit")


@admin_bp.route("/product/delete/<int:product_id>", methods=["POST"])
@admin_required
def delete_product_route(product_id):
    product = get_product_by_id(product_id)
    if not product:
        flash("Product not found.", "danger")
        return redirect(url_for("admin.products"))
    delete_product(product_id)
    log_action("DELETE_PRODUCT", f"Deleted ID {product_id}: {product['name']}")
    flash(f"Product '{product['name']}' deleted.", "info")
    return redirect(url_for("admin.products"))


def _collect_form():
    d = {k: request.form.get(k, "").strip()
         for k in ["name","category","description","price","stock",
                   "image","brand","weight","material","size","grade"]}
    try:
        d["price"] = float(d["price"])
        d["stock"] = int(d["stock"])
    except ValueError:
        flash("Price and stock must be valid numbers.", "danger")
        return None
    return d


# ── Orders 

@admin_bp.route("/orders")
@admin_required
def orders():
    return render_template("admin/admin_orders.html", orders=get_all_orders())


@admin_bp.route("/orders/update_status/<int:order_id>", methods=["POST"])
@admin_required
def update_order(order_id):
    update_order_status(order_id, request.form.get("status", "Confirmed"))
    flash("Order status updated.", "success")
    return redirect(url_for("admin.orders"))


# ── Messages 

@admin_bp.route("/messages")
@admin_required
def messages():
    return render_template("admin/admin_messages.html", messages=get_all_messages())


@admin_bp.route("/messages/delete/<int:msg_id>", methods=["POST"])
@admin_required
def delete_msg(msg_id):
    delete_message(msg_id)
    flash("Message deleted.", "info")
    return redirect(url_for("admin.messages"))


# ── CSV Exports 

@admin_bp.route("/export/orders")
@admin_required
def export_orders():
    return csv_response("cricketzone_orders.csv",
        ["order_id","customer_name","customer_email","customer_phone",
         "product_name","quantity","total_price","address","status","created_at"],
        get_all_orders())


@admin_bp.route("/export/products")
@admin_required
def export_products():
    return csv_response("cricketzone_products.csv",
        ["id","name","category","description","price","stock",
         "brand","weight","material","size","grade","created_at"],
        get_all_products())


@admin_bp.route("/export/messages")
@admin_required
def export_messages():
    return csv_response("cricketzone_messages.csv",
        ["id","name","email","subject","message","created_at"],
        get_all_messages())