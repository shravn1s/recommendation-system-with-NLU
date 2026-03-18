from dataset.products import products

PRODUCT_BY_ID = {p["id"]: p for p in products}


# ---------- NORMALIZATION HELPERS ----------

def normalize_price(price, max_price=1000):
    if price is None:
        return 0
    return price / max_price


def normalize_color(color):
    if not color:
        return ""

    c = color.lower()

    if "black" in c:
        return "black"
    if "chrome" in c:
        return "chrome"
    if "nickel" in c:
        return "nickel"
    if "white" in c:
        return "white"

    return c.strip()


def normalize_text(text):
    return text.lower().strip() if text else ""


# ---------- VECTOR CREATION ----------

def product_to_vector(p):
    return {
        "price": normalize_price(p.get("price")),
        "category": normalize_text(p.get("category")),
        "color": normalize_color(p.get("color")),
        "collection": normalize_text(p.get("collection"))
    }


# ---------- SIMILARITY ----------

def compute_similarity(p1, p2):

    weights = {
        "price": 0.2,
        "category": 0.4,
        "color": 0.2,
        "collection": 0.2
    }

    score = 0

    # price similarity
    score += weights["price"] * (1 - abs(p1["price"] - p2["price"]))

    # categorical matches
    if p1["category"] == p2["category"]:
        score += weights["category"]

    if p1["color"] == p2["color"]:
        score += weights["color"]

    if p1["collection"] == p2["collection"]:
        score += weights["collection"]

    return score


# ---------- EXPLANATION ----------

def explain(anchor, p):

    reasons = []

    if anchor.get("category") == p.get("category"):
        reasons.append("Same category")

    if normalize_color(anchor.get("color")) == normalize_color(p.get("color")):
        reasons.append("Similar finish")

    if anchor.get("collection") == p.get("collection"):
        reasons.append("Same collection")

    if anchor.get("price") and p.get("price"):
        if abs(anchor["price"] - p["price"]) < 50:
            reasons.append("Similar price")

    return reasons


# ---------- MAIN RECOMMENDER ----------

def recommend_products(anchor_id, limit=8):

    anchor = PRODUCT_BY_ID.get(anchor_id)

    if not anchor:
        return []

    anchor_vec = product_to_vector(anchor)

    scored = []

    for p in products:

        if p["id"] == anchor_id:
            continue

        vec = product_to_vector(p)
        sim = compute_similarity(anchor_vec, vec)

        p_copy = p.copy()
        p_copy["score"] = sim
        p_copy["reason"] = explain(anchor, p)

        scored.append((sim, p_copy))

    # sort by similarity (highest first)
    scored.sort(key=lambda x: x[0], reverse=True)

    # ---------- DIVERSITY ----------
    final = []
    used_categories = set()

    for sim, p in scored:

        # allow some diversity but still keep relevance
        if p["category"] not in used_categories or len(final) < 3:
            final.append(p)
            used_categories.add(p["category"])

        if len(final) >= limit:
            break

    return final
    