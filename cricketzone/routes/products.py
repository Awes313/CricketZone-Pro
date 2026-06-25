"""
cricketzone/routes/products.py — Product Catalogue
"""

from flask import Blueprint, render_template, abort
from cricketzone.models import (
    get_all_products, get_product_by_id, get_products_by_brand
)

products_bp = Blueprint("products", __name__)


@products_bp.route("/bats")
def bats():
    return render_template("products/bats.html",
        products=get_all_products("bat"), category="Cricket Bats")


@products_bp.route("/balls")
def balls():
    return render_template("products/bowls.html",
        products=get_all_products("ball"), category="Cricket Balls")


@products_bp.route("/kits")
def kits():
    return render_template("products/kits.html",
        products=get_all_products("kit"), category="Cricket Kits")


@products_bp.route("/product/<int:product_id>")
def product_detail(product_id):
    product = get_product_by_id(product_id)
    if not product:
        abort(404)
    # Same brand, same category products (excluding current)
    same_brand = get_products_by_brand(
        product["brand"], product["category"], product_id
    )
    return render_template("products/product_detail.html",
        product=product, same_brand=same_brand)