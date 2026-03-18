import os
import re
import requests
from dotenv import load_dotenv
from dataset.products import products

print("THIS IS FINAL WORKING AI SERVICE")

# ---------------- LOAD ENV ----------------
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")

# ---------------- PRODUCT LOOKUP ----------------
PRODUCT_BY_ID = {p["id"]: p for p in products}


# ---------------- RETRIEVER ----------------
def retrieve_products(query, limit=20):

    q = query.lower()

    is_all = "all" in q
    is_small = "small" in q or "compact" in q

    category_filter = None

    if "faucet" in q:
        category_filter = "faucet"
    elif "shower" in q:
        category_filter = "shower"
    elif "toilet" in q:
        category_filter = "toilet"
    elif "bathtub" in q or "tub" in q:
        category_filter = "bath"

    # -------- CASE 1: ALL --------
    if is_all and category_filter:
        return [
            p for p in products
            if category_filter in p["category"].lower()
        ]

    # -------- CASE 2: SMALL --------
    if is_small:
        return products[:20]

    # -------- CASE 3: NORMAL --------
    results = []

    for p in products:

        score = 0

        name = p.get("name", "").lower()
        category = p.get("category", "").lower()
        color = p.get("color", "").lower()
        collection = p.get("collection", "").lower()

        if category_filter and category_filter not in category:
            continue

        for w in q.split():
            if w in name:
                score += 3
            if w in category:
                score += 5
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

    # -------- STEP 1: RETRIEVE --------
    retrieved = retrieve_products(user_msg)

    if not retrieved:
        retrieved = products[:20]

    print("RETRIEVED:", [p["name"] for p in retrieved])

    # -------- STEP 2: BUILD CONTEXT --------
    context = "\n".join([
        f"ID: {p['id']}, Name: {p['name']}, Category: {p['category']}"
        for p in retrieved
    ])

    system_instruction = f"""
You are a friendly Kohler product assistant.

Here are some products:
{context}

Rules:
- Recommend ONLY from these products
-DO NOT mention IDS inside sentences
-DO NOT write (ID: 1,2,3) anywhere
-ALWAYS include IDS at the end

RESPONSE FORMAT:
Write a short helpful sentence(1-2 lines)

Then on a NEW LINE write:
IDS: [id1, id2, id3]

Example:
Here are some great faucet options for your space.
IDS: [1,2,3]
"""

    text = ""

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_msg}
                ],
                "temperature": 0.3
            },
            timeout=10,
            verify=False
        )

        data = response.json()
        print("RAW API RESPONSE:", data)

        if "choices" in data and len(data["choices"]) > 0:
            text = data["choices"][0]["message"].get("content", "").strip()
        elif "error" in data:
            print("API ERROR:", data["error"])
        else:
            print("UNKNOWN RESPONSE:", data)

    except Exception as e:
        print("HTTP ERROR:", e)

    # -------- ALWAYS HAVE TEXT --------
    if not text:
        text = "Here are some products you might like based on your request."

    print("AI TEXT:", text)

    # -------- STEP 3: EXTRACT IDS --------
    ids = []

    match = re.search(r"IDS:\s*\[(.*?)\]", text)
    if match:
        ids = [int(x.strip()) for x in match.group(1).split(",") if x.strip().isdigit()]

    # -------- REMOVE IDS FROM UI --------
    text = re.sub(r"IDS:\s*\[.*?\]", "", text).strip()

    # -------- STEP 4: CONTROL COUNT --------
    show_all = "all" in user_msg.lower()

    if not show_all:
        ids = ids[:6]

    # -------- STEP 5: FALLBACK --------
    if not ids:
        if show_all:
            ids = [p["id"] for p in retrieved]
        else:
            ids = [p["id"] for p in retrieved[:6]]

    # -------- STEP 6: MAP --------
    products_found = [PRODUCT_BY_ID.get(i) for i in ids if PRODUCT_BY_ID.get(i)]

    if not products_found:
        products_found = retrieved[:6]

    print("FINAL PRODUCTS:", [p["name"] for p in products_found])

    return text, products_found, []