from services.ai_service import normalized_products


# ---------------- RECOMMEND PRODUCTS ----------------
def recommend_products(query=None, anchor_id=None, limit=8):

    try:
        results = []

        # ---------------- QUERY MODE ----------------
        if query:
            q = query.lower()

            for p in normalized_products:
                score = 0

                text = f"{p['name']} {p['category']} {p['color']}".lower()

                # keyword match
                for word in q.split():
                    if word in text:
                        score += 2

                # intent boost
                if "small" in q or "compact" in q:
                    score += 2
                if "modern" in q:
                    score += 2
                if "premium" in q or "luxury" in q:
                    score += 3

                if score > 0:
                    results.append((score, p))

        # ---------------- ANCHOR MODE ----------------
        elif anchor_id:
            anchor = next(
                (p for p in normalized_products if str(p["id"]) == str(anchor_id)),
                None
            )

            if not anchor:
                return normalized_products[:limit]

            # recommend same category
            results = [
                (1, p) for p in normalized_products
                if p["category"] == anchor["category"]
                and p["id"] != anchor["id"]
            ]

        # ---------------- FALLBACK ----------------
        else:
            return normalized_products[:limit]

        # ---------------- SORT ----------------
        results.sort(key=lambda x: x[0], reverse=True)
        ranked = [p for _, p in results]

        # ---------------- DIVERSITY ----------------
        final = []
        seen = set()

        for p in ranked:
            if p["category"] not in seen:
                final.append(p)
                seen.add(p["category"])

            if len(final) >= limit:
                break

        # fill remaining
        if len(final) < limit:
            for p in ranked:
                if p not in final:
                    final.append(p)
                if len(final) >= limit:
                    break

        return final[:limit]

    except Exception as e:
        print("RECOMMEND ERROR:", e)
        return normalized_products[:limit]