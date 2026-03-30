from flask import Blueprint, request, jsonify, session
from services.cart_services import group_cart
from services.ai_service import normalized_products

cart_bp = Blueprint("cart", __name__)


# ---------------- HELPER: VALIDATE PRODUCT ----------------
def is_valid_product(pid):
    return any(str(p["id"]) == str(pid) for p in normalized_products)


# ---------------- ADD TO CART ----------------
@cart_bp.route("/add_to_cart", methods=["POST"])
def add_to_cart():

    pid = request.form.get("id")

    if not pid:
        return jsonify({"error": "Missing product id"}), 400

    pid = str(pid)

    # ✅ VALIDATION (NEW)
    if not is_valid_product(pid):
        return jsonify({"error": "Invalid product id"}), 400

    cart = session.get("cart")

    if not isinstance(cart, dict):
        cart = {}

    cart[pid] = cart.get(pid, 0) + 1

    session["cart"] = cart

    return jsonify({"status": "added"})


# ---------------- REMOVE ONE ----------------
@cart_bp.route("/remove_from_cart", methods=["POST"])
def remove_from_cart():

    pid = request.form.get("id")

    if not pid:
        return jsonify({"error": "Missing product id"}), 400

    pid = str(pid)

    cart = session.get("cart", {})

    if pid in cart:
        cart[pid] -= 1
        if cart[pid] <= 0:
            del cart[pid]

    session["cart"] = cart

    return jsonify({"status": "removed"})


# ---------------- REMOVE ALL ----------------
@cart_bp.route("/remove_all_from_cart", methods=["POST"])
def remove_all_from_cart():

    pid = request.form.get("id")

    if not pid:
        return jsonify({"error": "Missing product id"}), 400

    pid = str(pid)

    cart = session.get("cart", {})

    if pid in cart:
        del cart[pid]

    session["cart"] = cart

    return jsonify({"status": "removed_all"})


# ---------------- GET CART ----------------
@cart_bp.route("/get_cart")
def get_cart():

    cart = session.get("cart")

    if not isinstance(cart, dict):
        cart = {}

    # ✅ CRITICAL: variant-aware grouping
    data = group_cart(cart)

    return jsonify(data)


# ---------------- CLEAR CART ----------------
@cart_bp.route("/clear_cart", methods=["POST"])
def clear_cart():

    session["cart"] = {}

    return jsonify({"success": True})
