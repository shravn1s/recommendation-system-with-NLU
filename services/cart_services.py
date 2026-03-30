import re
from services.ai_service import normalized_products


# ---------------- BUILD LOOKUP ----------------
PRODUCT_BY_ID = {str(p["id"]): p for p in normalized_products}


# ---------------- GROUP CART ----------------
def group_cart(cart):

    items = []
    subtotal = 0

    for pid, qty in cart.items():

        pid = str(pid)  # ensure string key

        p = PRODUCT_BY_ID.get(pid)
        if not p:
            continue

        # ---------------- SAFE PRICE PARSE ----------------
        price_raw = p.get("price", 0)

        if isinstance(price_raw, str):
            # remove anything not digit or dot
            cleaned = re.sub(r"[^\d.]", "", price_raw)
            price = float(cleaned) if cleaned else 0.0
        else:
            price = float(price_raw)

        # ---------------- CALCULATIONS ----------------
        line_total = round(price * qty, 2)
        subtotal += line_total

        # ---------------- ITEM STRUCTURE ----------------
        items.append(
            {
                "id": p["id"],
                "base_id": p.get("base_id"),
                "name": p["name"],
                "color": p.get("color", ""),
                "price": price,
                "image": p.get("image"),
                "product_link": p.get("product_link"),
                # ✅ match frontend expectations
                "quantity": qty,
                "total": line_total,
            }
        )

    # ---------------- TOTALS ----------------
    subtotal = round(subtotal, 2)
    gst = round(subtotal * 0.18, 2)
    total = round(subtotal + gst, 2)

    return {
        "items": items,
        "count": sum(i["quantity"] for i in items),
        "subtotal": subtotal,
        "gst": gst,
        "total": total,
    }
