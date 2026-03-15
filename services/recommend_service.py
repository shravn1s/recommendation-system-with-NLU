from dataset.products import products

PRODUCT_BY_ID = {p["id"]: p for p in products}


def recommend_products(anchor_id, limit=8):

    anchor = PRODUCT_BY_ID.get(anchor_id)

    if not anchor:
        return []

    same_collection = []
    same_color = []
    same_category = []

    for p in products:

        if p["id"] == anchor_id:
            continue

        if p.get("collection") == anchor.get("collection"):
            same_collection.append(p)

        elif p.get("color") == anchor.get("color"):
            same_color.append(p)

        elif p.get("category") == anchor.get("category"):
            same_category.append(p)

    results = same_collection + same_color + same_category

    return results[:limit]