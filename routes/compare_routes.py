from flask import Blueprint, request, jsonify, session
from services.ai_service import normalized_products
import re
import requests
import os
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

compare_bp = Blueprint("compare", __name__)

# ---------------- LOOKUP ----------------
PRODUCT_BY_ID = {str(p["id"]): p for p in normalized_products}


# ---------------- SESSION HELPER ----------------
def ensure_compare():
    if "compare" not in session:
        session["compare"] = []
    return session["compare"]


# ---------------- AI COMPARE ----------------
@compare_bp.route("/compare_ai", methods=["GET"])
def compare_ai():

    comp = ensure_compare()
    items = [PRODUCT_BY_ID[i] for i in comp if i in PRODUCT_BY_ID]

    if len(items) < 2:
        return jsonify({"explanation": "Select at least 2 products to compare."})

    # -------- CLEAN PRICE --------
    def clean_price(p):
        raw = p.get("price", 0)
        if isinstance(raw, str):
            cleaned = re.sub(r"[^\d.]", "", raw)
            return float(cleaned) if cleaned else 0
        return float(raw)

    # -------- BUILD PROMPT --------
    prompt = "Compare these products clearly:\n\n"

    for p in items:
        prompt += f"""
Name: {p.get('name')}
Price: {clean_price(p)}
Category: {p.get('category')}
Color: {p.get('color')}

Description:
{p.get('main_description', '')}

Features:
{p.get('features', '')}

Dimensions:
{p.get('dimensions', '')}

---
"""

    prompt += """
Explain:
1. Key differences
2. Which is best for what use-case
3. Value for money
Keep it short and user-friendly.
"""

    # -------- GROQ CALL --------
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a product expert. Compare clearly with pros/cons and recommend best option.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.5,
        },
    )

    data = response.json()

    # 🔥 DEBUG (VERY IMPORTANT)
    print("GROQ RESPONSE:", data)

    # -------- ERROR HANDLING --------
    if "choices" not in data:
        return jsonify({"explanation": f"AI Error: {data}"})

    explanation = data["choices"][0]["message"]["content"]

    return jsonify({"explanation": explanation})


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

    items = [PRODUCT_BY_ID[i] for i in comp if i in PRODUCT_BY_ID]

    return jsonify({"items": items})


# ---------------- CLEAR ----------------
@compare_bp.route("/compare_clear", methods=["POST"])
def compare_clear():

    session["compare"] = []

    return jsonify({"compare": []})
