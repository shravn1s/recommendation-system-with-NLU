from flask import Blueprint, jsonify, request, session
from services.recommend_service import recommend_products
from dataset.products import products
from dataset.specs import SPEC_BY_SKU

recommend_bp = Blueprint("recommend", __name__)

# Fast product lookup
PRODUCT_BY_ID = {p["id"]: p for p in products}


# ---------- Helpers ----------

def shape_product(product):
    return {
        "id": product.get("id"),
        "name": product.get("name"),
        "price": product.get("price"),
        "color": product.get("color"),
        "image": product.get("image"),
        "category": product.get("category"),
        "collection": product.get("collection"),
        "sku": product.get("sku"),
        "spec_mode": SPEC_BY_SKU.get(product.get("sku"), "Specification not available"),
    }


def ensure_recent():
    if "recent" not in session:
        session["recent"] = []

    # Remove invalid product IDs
    session["recent"] = [pid for pid in session["recent"] if pid in PRODUCT_BY_ID]

    return session["recent"]


# ---------- Recently Viewed ----------

@recommend_bp.route("/recent_add", methods=["POST"])
def recent_add():

    pid = int(request.form.get("id", 0))

    if pid not in PRODUCT_BY_ID:
        return jsonify({"ok": False, "error": "Invalid product"}), 400

    recent = ensure_recent()

    if pid in recent:
        recent.remove(pid)

    recent.insert(0, pid)

    # Keep only last 10
    del recent[10:]

    session.modified = True

    return jsonify({"ok": True, "recent": recent})


@recommend_bp.route("/recent_get")
def recent_get():

    recent = ensure_recent()
    session.modified = True

    items = [
        shape_product(PRODUCT_BY_ID[p])
        for p in recent
        if p in PRODUCT_BY_ID
    ]

    return jsonify({
        "ok": True,
        "items": items
    })


# ---------- Recommendations ----------

@recommend_bp.route("/recommend_get")
def recommend_get():

    limit = int(request.args.get("limit", 8))

    recent = ensure_recent()

    # Cold start
    if not recent:
        return jsonify({
            "ok": True,
            "items": [shape_product(p) for p in products[:limit]]
        })

    anchor = recent[0]

    items = recommend_products(anchor)

    return jsonify({
        "ok": True,
        "items": [shape_product(p) for p in items[:limit]]
    })

    anchor = recent[0]

    items = recommend_products(anchor)

    return jsonify({
        "ok": True,
        "items": [shape_product(p) for p in items]
    })


# ---------- Personalization (Recent + Recommend) ----------

@recommend_bp.route("/personalize_get")
def personalize_get():

    recent = ensure_recent()

    recent_items = [
        shape_product(PRODUCT_BY_ID[p])
        for p in recent
        if p in PRODUCT_BY_ID
    ]

    if not recent:
        recommend_items = [shape_product(p) for p in products[:8]]
    else:
        anchor = recent[0]
        recommend_items = [
            shape_product(p)
            for p in recommend_products(anchor)
        ]

    return jsonify({
        "ok": True,
        "recent": recent_items,
        "recommend": recommend_items
    })


# ---------- Get Single Product ----------

@recommend_bp.route("/product_get")
def product_get():

    pid = int(request.args.get("id", 0))

    product = PRODUCT_BY_ID.get(pid)

    if not product:
        return jsonify({
            "ok": False,
            "error": "Product not found"
        }), 404

    return jsonify({
        "ok": True,
        "item": shape_product(product)
    })

# ---------- Browse All Products ----------

@recommend_bp.route("/browse_all")
def browse_all():

    return jsonify({
        "ok": True,
        "products": [shape_product(p) for p in products]
    })   