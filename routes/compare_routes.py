from flask import Blueprint, request, jsonify, session
from dataset.products import products

compare_bp = Blueprint("compare", __name__)

PRODUCT_BY_ID = {p["id"]: p for p in products}

def ensure_compare():
    if "compare" not in session:
        session["compare"] = []
    return session["compare"]


@compare_bp.route("/compare_add", methods=["POST"])
def compare_add():

    pid = int(request.form.get("id", 0))
    comp = ensure_compare()

    if pid in comp:
        return jsonify({"compare": comp})

    # limit compare to 3 products
    if len(comp) >= 3:
        return jsonify({"error": "Only 3 products allowed"}), 400

    comp.append(pid)

    session.modified = True

    return jsonify({"compare": comp})


@compare_bp.route("/compare_remove", methods=["POST"])
def compare_remove():
    pid = int(request.form.get("id", 0))
    comp = ensure_compare()

    if pid in comp:
        comp.remove(pid)

    session.modified = True
    return jsonify({"compare": comp})


@compare_bp.route("/compare_get")
def compare_get():
    comp = ensure_compare()

    items = [PRODUCT_BY_ID[i] for i in comp if i in PRODUCT_BY_ID]

    return jsonify({"items": items})


@compare_bp.route("/compare_clear", methods=["POST"])
def compare_clear():
    session["compare"] = []
    return jsonify({"compare": []})