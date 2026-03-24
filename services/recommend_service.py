from dataset.products import products

PRODUCT_BY_ID = {p["id"]: p for p in products}


def recommend_products(anchor_id, limit=8):

    anchor = PRODUCT_BY_ID.get(anchor_id)
    if not anchor:
        return []

    results = []

    for p in products:
        if p["id"] == anchor_id:
            continue

        score = 0

        # Feature 1: Collection match
        if p.get("collection") == anchor.get("collection"):
            score += 5

        # Feature 2: Color match
        if p.get("color") == anchor.get("color"):
            score += 3

        # Feature 3: Category match
        if p.get("category") == anchor.get("category"):
            score += 2

        # Feature 4: Price similarity (NEW)
        if p.get("price") and anchor.get("price"):
            diff = abs(p["price"] - anchor["price"])
            if diff < 50:
                score += 2
            elif diff < 100:
                score += 1

        if score > 0:
            results.append((score, p))

    # Sort by highest score
    results.sort(key=lambda x: x[0], reverse=True)

    return [p for score, p in results[:limit]]