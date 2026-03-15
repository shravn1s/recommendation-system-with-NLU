from dataset.products import products

PRODUCT_BY_ID = {p["id"]: p for p in products}


def group_cart(cart):

    items = []
    subtotal = 0

    for pid, qty in cart.items():

        pid = int(pid)
        p = PRODUCT_BY_ID.get(pid)

        if p is None:
            continue

        line_total = (p["price"] * qty) if p["price"] else 0
        subtotal += line_total

        items.append({
            "id": p["id"],
            "name": p["name"],
            "color": p["color"],
            "price": p["price"],
            "image": p["image"],
            "qty": qty,
            "line_total": line_total
        })

    gst = subtotal * 0.18
    total = subtotal + gst

    return {
        "items": items,
        "count": sum(i["qty"] for i in items),
        "subtotal": subtotal,
        "gst": gst,
        "total": total
    }