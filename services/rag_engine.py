import math
import re


# ---------------- TOKENIZE ----------------
def tokenize(text):
    return re.findall(r'\w+', text.lower())


def vectorize(tokens):
    vec = {}
    for t in tokens:
        vec[t] = vec.get(t, 0) + 1
    return vec


def cosine(v1, v2):
    common = set(v1) & set(v2)
    num = sum(v1[w] * v2[w] for w in common)

    d1 = math.sqrt(sum(v * v for v in v1.values()))
    d2 = math.sqrt(sum(v * v for v in v2.values()))

    return num / (d1 * d2) if d1 and d2 else 0


# ---------------- INTENT EXPANSION ----------------
def expand_query(query):
    q = query.lower()
    extra = []

    if "small" in q or "compact" in q:
        extra += ["compact", "small", "space", "saving"]

    if "modern" in q:
        extra += ["modern", "sleek"]

    if "luxury" in q or "premium" in q:
        extra += ["premium", "luxury"]

    return q + " " + " ".join(extra)


# ---------------- RAG ENGINE ----------------
class RAGEngine:
    def __init__(self, products):
        self.products = products
        self.vectors = []

        for p in products:
            text = self._build_text(p)
            tokens = tokenize(text)
            vec = vectorize(tokens)
            self.vectors.append(vec)

    # ---------------- BUILD TEXT ----------------
    def _build_text(self, p):
        return " ".join([
            (str(p.get("name", "")) + " ") * 3,
            (str(p.get("category", "")) + " ") * 4,
            (str(p.get("color", "")) + " ") * 2,
            str(p.get("description", "")),
        ])

    # ---------------- DETECT CATEGORY ----------------
    def _detect_category(self, query):
        q = query.lower()

        if "toilet" in q:
            return "toilets"
        if "sink" in q or "basin" in q:
            return "sinks"
        if "faucet" in q or "tap" in q:
            return "faucets"
        if "shower" in q:
            return "showers"
        if "bath" in q:
            return "bathtubs"

        return None

    # ---------------- SEARCH ----------------
    def search_products(self, query, limit=10):

        query = expand_query(query)
        q_vec = vectorize(tokenize(query))

        intent_category = self._detect_category(query)

        scores = []

        for i, v in enumerate(self.vectors):
            score = cosine(q_vec, v)

            product = self.products[i]
            category = (product.get("category") or "").lower()

            # -------- CATEGORY BOOST --------
            if intent_category:
                if intent_category == category:
                    score += 0.5
                else:
                    score *= 0.4

            scores.append((score, i))

        scores.sort(key=lambda x: x[0], reverse=True)

        results = []

        for score, i in scores:
            if score < 0.08:
                continue

            results.append(self.products[i])

            if len(results) >= limit:
                break

        # -------- FALLBACK --------
        if not results:
            if intent_category:
                results = [
                    p for p in self.products
                    if p["category"] == intent_category
                ][:limit]
            else:
                results = self.products[:limit]

        return results

    # ---------------- SIMILAR PRODUCTS ----------------
    def get_similar_products(self, product_id, limit=10):

        idx = next(
            (i for i, p in enumerate(self.products)
             if str(p["id"]) == str(product_id)),
            None
        )

        if idx is None:
            return []

        base_vec = self.vectors[idx]

        scores = []

        for i, v in enumerate(self.vectors):
            if i == idx:
                continue

            score = cosine(base_vec, v)
            scores.append((score, i))

        scores.sort(key=lambda x: x[0], reverse=True)

        return [self.products[i] for _, i in scores[:limit]]


# ---------------- GLOBAL INSTANCE ----------------
rag_engine = None


def init_rag(products):
    global rag_engine
    rag_engine = RAGEngine(products)


def get_rag():
    return rag_engine