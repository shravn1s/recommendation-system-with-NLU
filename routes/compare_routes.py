from flask import Blueprint, request, jsonify, session
from services.ai_service import normalized_products

compare_bp = Blueprint("compare", __name__)


# ---------------- LOOKUP ----------------
PRODUCT_BY_ID = {
    str(p["id"]): p for p in normalized_products
}


# ---------------- SHAPE PRODUCT ----------------
def shape_product(p):
    return {
        "id": p.get("id"),
        "base_id": p.get("base_id"),
        "name": p.get("name"),
        "price": p.get("price"),
        "color": p.get("color"),
        "image": p.get("image"),
        "category": p.get("category"),
        "product_link": p.get("product_link"),
    }


# ---------------- SESSION HELPER ----------------
def ensure_compare():
    if "compare" not in session:
        session["compare"] = []
    return session["compare"]


# ---------------- ADD ----------------
@compare_bp.route("/compare_add", methods=["POST"])
def compare_add():

    pid = request.form.get("id")

    if not pid:
        return jsonify({"error": "Missing product id"}), 400

    pid = str(pid)

    if pid not in PRODUCT_BY_ID:
        return jsonify({"error": "Invalid product"}), 400

    comp = ensure_compare()

    if pid in comp:
        return jsonify({"compare": comp})

    # limit = 3
    if len(comp) >= 3:
        return jsonify({"error": "Only 3 products allowed"}), 400

    comp.append(pid)

    session.modified = True

    return jsonify({"compare": comp})


# ---------------- REMOVE ----------------
@compare_bp.route("/compare_remove", methods=["POST"])
def compare_remove():

    pid = request.form.get("id")

    if not pid:
        return jsonify({"error": "Missing product id"}), 400

    pid = str(pid)

    comp = ensure_compare()

    if pid in comp:
        comp.remove(pid)

    session.modified = True

    return jsonify({"compare": comp})


# ---------------- GET ----------------
@compare_bp.route("/compare_get")
def compare_get():

    comp = ensure_compare()

    items = [
        shape_product(PRODUCT_BY_ID[i])
        for i in comp
        if i in PRODUCT_BY_ID
    ]

    return jsonify({"items": items})


# ---------------- CLEAR ----------------
@compare_bp.route("/compare_clear", methods=["POST"])
def compare_clear():

    session["compare"] = []

    return jsonify({"compare": []})