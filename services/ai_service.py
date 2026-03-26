import json
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")


# ==============================
# LOAD + CORRECT NORMALIZATION
# ==============================

def load_products():
    with open("dataset/products.json", "r") as f:
        raw_data = json.load(f)

    normalized = []

    def traverse(node, path=None):
        if path is None:
            path = []

        if isinstance(node, dict):

            # ✅ PRODUCT NODE
            if "variants" in node:

                # 🔥 CORRECT COLLECTION
                collection = node.get("name", "").strip()

                # 🔥 STRICT CATEGORY
                category = None
                for p in path:
                    p = p.lower()

                    if "toilet" in p:
                        category = "toilet"
                    elif "faucet" in p:
                        category = "faucet"
                    elif "sink" in p:
                        category = "sink"
                    elif "shower" in p:
                        category = "shower"
                    elif "bath" in p:
                        category = "bathtub"

                # 🚨 DO NOT ADD IF CATEGORY UNKNOWN
                if not category:
                    return

                for vid, variant in node["variants"].items():
                    normalized.append({
                        "id": str(variant.get("product_id", vid)),
                        "name": collection,
                        "collection": collection,
                        "category": category,
                        "color": (variant.get("color") or "").lower(),
                        "price": variant.get("price", 0),
                        "image": variant.get("image", ""),
                        "product_link": variant.get("link", ""),   # ✅ COMMA ADDED
                        "description": node.get("detailed", ""),
                        "dimensions": node.get("dimensions", "")
                    })

            # continue traversal
            for k, v in node.items():
                traverse(v, path + [k])

        elif isinstance(node, list):
            for item in node:
                traverse(item, path)

    traverse(raw_data)

    print(f"✅ Loaded {len(normalized)} clean products")

    return normalized


normalized_products = load_products()


# ==============================
# QUERY
# ==============================

def normalize_query(q):
    q = q.lower()

    fixes = {
        "shwer": "shower",
        "bathrom": "bathroom",
        "tolet": "toilet",
        "faucets": "faucet",
        "sinks": "sink",
        "toilets": "toilet",
        "bathtubs": "bathtub"
    }

    for k, v in fixes.items():
        q = q.replace(k, v)

    return q


def detect_category(q):
    if "toilet" in q:
        return "toilet"
    if "faucet" in q:
        return "faucet"
    if "sink" in q:
        return "sink"
    if "shower" in q:
        return "shower"
    if "bath" in q:
        return "bathtub"
    return None


# ==============================
# RETRIEVAL (STRICT + COLLECTION BASED)
# ==============================

def retrieve_products(query, limit=8):
    q = normalize_query(query)
    category = detect_category(q)

    # ❌ If category doesn't exist → return empty
    if not category:
        return []

    # filter strictly
    filtered = [p for p in normalized_products if p["category"] == category]

    if not filtered:
        return []

    # group by collection
    seen = set()
    final = []

    for p in filtered:
        col = p["collection"]

        if col not in seen:
            final.append(p)
            seen.add(col)

        if len(final) >= limit:
            break

    return final


# ==============================
# AI RESPONSE (CLEAN)
# ==============================

def generate_ai_response(user_msg):
    category = detect_category(user_msg)

    if not category:
        return (
            "We offer a wide range of bathroom and kitchen products including faucets, sinks, showers, bathtubs, and accessories.",
            [],
            []
        )

    products = retrieve_products(user_msg)

    if not products:
        return (
            f"We currently don’t have {category} products available.",
            [],
            []
        )

    collections = list({p["collection"] for p in products})

    text = f"Here are some {category} collections: " + ", ".join(collections[:5]) + "."

    return text, products, []