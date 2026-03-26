from services.ai_service import normalized_products


# ---------------- BUILD LOOKUP ----------------
PRODUCT_BY_ID = {
    str(p["id"]): p for p in normalized_products
}


# ---------------- GROUP CART ----------------
def group_cart(cart):

    items = []
    subtotal = 0

    for pid, qty in cart.items():

        pid = str(pid)  # ✅ FIX: keep string (variant id)

        p = PRODUCT_BY_ID.get(pid)

        if not p:
            continue

        price = float(p.get("price", 0))
        line_total = price * qty

        subtotal += line_total

        items.append({
            "id": p["id"],
            "base_id": p.get("base_id"),
            "name": p["name"],
            "color": p.get("color", ""),
            "price": price,
            "image": p.get("image"),
            "product_link": p.get("product_link"),
            "qty": qty,
            "line_total": line_total
        })

    gst = round(subtotal * 0.18, 2)
    total = round(subtotal + gst, 2)

    return {
        "items": items,
        "count": sum(i["qty"] for i in items),
        "subtotal": round(subtotal, 2),
        "gst": gst,
        "total": total
    }