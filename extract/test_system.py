import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from services.ai_service import generate_ai_response


def evaluate_query(query):
    text, products, _ = generate_ai_response(query)

    categories = [p.get("category", "").lower() for p in products]

    return {
        "query": query,
        "response": text,
        "products": [p["name"] for p in products],
        "categories": categories
    }


def analyze(result):
    issues = []

    cats = result["categories"]

    # -------- ISSUE 1: NO RESULTS --------
    if not result["products"]:
        issues.append("NO_PRODUCTS")

    # -------- ISSUE 2: SAME CATEGORY REPETITION --------
    if len(set(cats)) == 1 and len(cats) > 2:
        issues.append("NO_DIVERSITY")

    # -------- ISSUE 3: WEAK RESPONSE --------
    if len(result["response"]) < 50:
        issues.append("WEAK_RESPONSE")

    # -------- ISSUE 4: GENERIC LANGUAGE --------
    bad_phrases = ["well suited", "great option", "good for", "these products"]
    if any(b in result["response"].lower() for b in bad_phrases):
        issues.append("GENERIC_AI")

    return issues


def main():
    import os

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    with open(os.path.join(BASE_DIR, "queries.json")) as f:
        queries = json.load(f)

    all_results = []
    summary = {}

    for q in queries:
        result = evaluate_query(q)
        issues = analyze(result)

        # store full result
        entry = {
            "query": q,
            "response": result["response"],
            "products": result["products"],
            "categories": result["categories"],
            "issues": issues
        }

        all_results.append(entry)

        # build summary
        for issue in issues:
            summary[issue] = summary.get(issue, 0) + 1

    # -------- SAVE RESULTS --------
    output = {
        "summary": summary,
        "results": all_results
    }

    output_path = os.path.join(BASE_DIR, "system_results.json")

    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n✅ Results saved to: {output_path}")


if __name__ == "__main__":
    main()