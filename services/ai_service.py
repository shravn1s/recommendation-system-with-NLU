import os
import re
import google.generativeai as genai
from dataset.products import products

# ---------------- GEMINI SETUP ----------------

API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-flash-latest")

# ---------------- SYSTEM PROMPT ----------------

product_context = str(products)

system_instruction = f"""
You are a Kohler product sales assistant.

Inventory:
{product_context}

Rules:
- Recommend ONLY products from the inventory.
- Keep responses short (2–3 lines).
- Never invent product names.
-If the user request is vague (example: "something for my bathroom"),
  ask a clarification question instead of recommending products.
- Always end with: "Showing items below."
- Always include product IDs.

Format:
Short response.

IDS: [id1,id2,id3]
"""

# ---------------- PRODUCT LOOKUP ----------------

PRODUCT_BY_ID = {p["id"]: p for p in products}

# ---------------- PRICE EXTRACTION ----------------

def extract_price(query):
    match = re.search(r"\$(\d+)", query)
    if match:
        return int(match.group(1))
    return None

# ---------------- SMART PRODUCT SEARCH ----------------

def search_products(query, limit=5):

    q = query.lower()
    words = q.split()

    price_match = re.search(r"(under|below)\s*(\d+)", q)
    max_price = float(price_match.group(2)) if price_match else None

    results = []

    for p in products:

        score = 0

        name = str(p.get("name", "")).lower()
        category = str(p.get("category", "")).lower()
        color = str(p.get("color", "")).lower()
        collection = str(p.get("collection", "")).lower()

        price = p.get("price")

        # safe price filtering
        if max_price is not None and price is not None:
            if price > max_price:
                continue

        for w in words:

            if w in name:
                score += 3

            if w in category:
                score += 2

            if w in color:
                score += 2

            if w in collection:
                score += 2

        if score > 0:
            results.append((score, p))

    results.sort(key=lambda x: x[0], reverse=True)

    return [p for score, p in results[:limit]]

# ---------------- AI RESPONSE ----------------

def generate_ai_response(user_msg):

    prompt = f"{system_instruction}\n\nUser: {user_msg}\nAssistant:"

    # SAFE GEMINI CALL
    try:
        response = model.generate_content(prompt)
        text = response.text if hasattr(response, "text") else str(response)
    except Exception as e:
        print("Gemini error:", e)
        text = "Here are some products you might like. Showing items below."

    ids = []
    compare_ids = []

    # normal product IDS
    match = re.search(r"IDS:\s*\[(.*?)\]", text)
    if match:
        id_string = match.group(1)

        # LIMIT TO 6 PRODUCTS
        ids = [int(x.strip()) for x in id_string.split(",") if x.strip().isdigit()][:6]

        text = text.replace(match.group(0), "").strip()

    # compare IDS
    compare_match = re.search(r"COMPARE:\s*\[(.*?)\]", text)
    if compare_match:
        id_string = compare_match.group(1)
        compare_ids = [int(x.strip()) for x in id_string.split(",") if x.strip().isdigit()]
        text = text.replace(compare_match.group(0), "").strip()

    # fallback search if AI fails
    # Only fallback if AI response explicitly looks like a product request
    if not ids and any(word in user_msg.lower() for word in ["show", "recommend", "find", "suggest"]):
        matched = search_products(user_msg)
        if matched:
            ids = [p["id"] for p in matched]

    products_found = [PRODUCT_BY_ID.get(i) for i in ids if PRODUCT_BY_ID.get(i)]

    return text, products_found, compare_ids