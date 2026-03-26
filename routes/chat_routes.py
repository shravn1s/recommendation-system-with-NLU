from flask import Blueprint, request, jsonify
from services.ai_service import generate_ai_response, retrieve_products, normalize_query

chat_bp = Blueprint("chat", __name__)


# ---------------- GREETING ----------------
def is_greeting(q):
    q = q.lower().strip()
    return any(x in q for x in [
        "hi", "hello", "hey", "good morning", "good evening"
    ])


# ---------------- QUERY VALIDATION ----------------
def is_valid_query(q):
    q = normalize_query(q)  # ✅ FIX: normalize before checking

    keywords = [
        "toilet", "sink", "faucet", "shower",
        "bathtub", "bath", "tap", "basin"
    ]

    generic = [
        "bathroom", "modern", "small", "luxury",
        "design", "setup", "products", "premium",
        "compact", "space"
    ]

    return any(k in q for k in keywords) or any(g in q for g in generic)


# ---------------- ROUTE ----------------
@chat_bp.route("/get_response", methods=["POST"])
def get_response():

    user_msg = request.form.get("msg", "").strip()

    try:
        # -------- GREETING --------
        if is_greeting(user_msg):
            return jsonify({
                "response": (
                    "Hi! I can help you explore Kohler toilets, faucets, sinks, showers, "
                    "and bathtubs. Try asking things like 'small bathroom', "
                    "'modern faucets', 'premium products', or 'bathtubs'."
                ),
                "products": [],   # keep empty (frontend handles this now)
                "compare_ids": []
            })

        # -------- LIGHT VALIDATION --------
        if not is_valid_query(user_msg):
            return jsonify({
                "response": (
                    "I can help with Kohler bathroom products like toilets, sinks, faucets, "
                    "showers, and bathtubs. Try something like 'modern bathroom', "
                    "'compact sink', or 'premium bathtub'."
                ),
                "products": [],
                "compare_ids": []
            })

        # -------- MAIN SYSTEM --------
        text, products, compare_ids = generate_ai_response(user_msg)

        # ✅ SAFETY: fallback if retrieval failed
        if not products:
            products = retrieve_products(user_msg)

        return jsonify({
            "response": text,
            "products": products,
            "compare_ids": compare_ids
        })

    except Exception as e:
        print("ERROR:", e)

        return jsonify({
            "response": "Something went wrong while processing your request.",
            "products": [],
            "compare_ids": []
        })