from flask import Blueprint, request, jsonify, session
from services.cart_services import group_cart

cart_bp = Blueprint("cart", __name__)


# Add product to cart
@cart_bp.route("/add_to_cart", methods=["POST"])
def add_to_cart():

    pid = request.form.get("id")

    if not pid:
        return jsonify({"error": "Missing product id"}), 400

    cart = session.get("cart")

    # FIX: ensure cart is always a dict
    if not isinstance(cart, dict):
        cart = {}

    pid = str(pid)

    cart[pid] = cart.get(pid, 0) + 1

    session["cart"] = cart

    return jsonify({"status": "added"})


# Remove one quantity
@cart_bp.route("/remove_from_cart", methods=["POST"])
def remove_from_cart():

    pid = request.form.get("id")

    cart = session.get("cart", {})

    if pid in cart:
        cart[pid] -= 1
        if cart[pid] <= 0:
            del cart[pid]

    session["cart"] = cart

    return jsonify({"status": "removed"})


# Remove product completely
@cart_bp.route("/remove_all_from_cart", methods=["POST"])
def remove_all_from_cart():

    pid = request.form.get("id")

    cart = session.get("cart", {})

    if pid in cart:
        del cart[pid]

    session["cart"] = cart

    return jsonify({"status": "removed_all"})


# Get cart data
@cart_bp.route("/get_cart")
def get_cart():

    cart = session.get("cart")

    if not isinstance(cart, dict):
        cart = {}

    data = group_cart(cart)

    return jsonify(data)

# Clear entire cart
@cart_bp.route("/clear_cart", methods=["POST"])
def clear_cart():

    session["cart"] = {}

    return jsonify({"status": "Cleared"})