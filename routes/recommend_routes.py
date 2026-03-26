from flask import Blueprint, jsonify, request, session
from services.ai_service import normalized_products

recommend_bp = Blueprint("recommend", __name__)


# ---------------- LOOKUP ----------------
PRODUCT_BY_ID = {
    str(p["id"]): p for p in normalized_products
}


# ---------------- SHAPE PRODUCT ----------------
def shape_product(product):
    return {
        "id": product.get("id"),
        "base_id": product.get("base_id"),
        "name": product.get("name"),
        "price": product.get("price"),
        "color": product.get("color"),
        "image": product.get("image"),
        "category": product.get("category"),
        "product_link": product.get("product_link"),
    }


# ---------------- ENSURE RECENT ----------------
def ensure_recent():
    if "recent" not in session:
        session["recent"] = []

    # keep only valid ids
    session["recent"] = [
        pid for pid in session["recent"]
        if str(pid) in PRODUCT_BY_ID
    ]

    return session["recent"]


# ---------------- ADD RECENT ----------------
@recommend_bp.route("/recent_add", methods=["POST"])
def recent_add():

    pid = request.form.get("id")

    if not pid or str(pid) not in PRODUCT_BY_ID:
        return jsonify({"ok": False, "error": "Invalid product"}), 400

    pid = str(pid)

    recent = ensure_recent()

    if pid in recent:
        recent.remove(pid)

    recent.insert(0, pid)

    del recent[10:]  # keep last 10

    session.modified = True

    return jsonify({"ok": True, "recent": recent})


# ---------------- GET RECENT ----------------
@recommend_bp.route("/recent_get")
def recent_get():

    recent = ensure_recent()
    session.modified = True

    items = [
        shape_product(PRODUCT_BY_ID[p])
        for p in recent
    ]

    return jsonify({
        "ok": True,
        "items": items
    })


# ---------------- BASIC RECOMMEND ----------------
@recommend_bp.route("/recommend_get")
def recommend_get():

    limit = int(request.args.get("limit", 8))
    recent = ensure_recent()

    # cold start
    if not recent:
        return jsonify({
            "ok": True,
            "items": [
                shape_product(p) for p in normalized_products[:limit]
            ]
        })

    # use last viewed as anchor
    anchor = recent[0]
    anchor_product = PRODUCT_BY_ID.get(anchor)

    if not anchor_product:
        return jsonify({
            "ok": True,
            "items": [
                shape_product(p) for p in normalized_products[:limit]
            ]
        })

    # simple similarity: same category
    same_category = [
        p for p in normalized_products
        if p["category"] == anchor_product["category"]
        and p["id"] != anchor
    ]

    results = same_category[:limit]

    return jsonify({
        "ok": True,
        "items": [shape_product(p) for p in results]
    })


# ---------------- PERSONALIZATION ----------------
@recommend_bp.route("/personalize_get")
def personalize_get():

    recent = ensure_recent()

    recent_items = [
        shape_product(PRODUCT_BY_ID[p])
        for p in recent
    ]

    if not recent:
        recommend_items = [
            shape_product(p) for p in normalized_products[:8]
        ]
    else:
        anchor = recent[0]
        anchor_product = PRODUCT_BY_ID.get(anchor)

        recommend_items = [
            shape_product(p)
            for p in normalized_products
            if p["category"] == anchor_product["category"]
            and p["id"] != anchor
        ][:8]

    return jsonify({
        "ok": True,
        "recent": recent_items,
        "recommend": recommend_items
    })


# ---------------- GET SINGLE PRODUCT ----------------
@recommend_bp.route("/product_get")
def product_get():

    pid = request.args.get("id")

    if not pid:
        return jsonify({"ok": False, "error": "Missing id"}), 400

    pid = str(pid)

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


# ---------------- BROWSE ALL ----------------
@recommend_bp.route("/browse_all")
def browse_all():

    return jsonify({
        "ok": True,
        "products": [
            shape_product(p) for p in normalized_products
        ]
    })