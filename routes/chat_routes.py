from flask import Blueprint, request, jsonify
from services.ai_service import generate_ai_response

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/get_response", methods=["POST"])
def get_response():

    user_msg = request.form["msg"]

    try:
        text, products, compare_ids = generate_ai_response(user_msg)

        return jsonify({
            "response": text,
            "products": products,
            "compare_ids": compare_ids
        })

    except Exception as e:
        print("AI ERROR:", e)

        return jsonify({
            "response": "Sorry, something went wrong.",
            "products": [],
            "compare_ids": []
        })