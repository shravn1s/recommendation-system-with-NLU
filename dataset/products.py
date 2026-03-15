# dataset/products.py
import csv
from html import unescape
from pathlib import Path

CSV_PATH = Path(__file__).resolve().parent / "main.csv"

SINGULAR = {"Faucets": "Faucet", "Showers": "Shower", "Toilets": "Toilet"}

def make_name(collection, category):
    return f"{collection} {SINGULAR.get(category, category)}"

products = []

with CSV_PATH.open(newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for i, r in enumerate(reader, start=1):

        products.append({
            "id": i,
            "name": make_name(unescape(r["Collection"]), unescape(r["Category"])),
            "price": float(r["Price USD"]) if r.get("Price USD") not in (None, "", "NaN") else None,
            "color": unescape(r["Finish"]),
            "image": unescape(r["Image URL"]),
            "category": unescape(r["Category"]),
            "collection": unescape(r["Collection"]),
            "sku": unescape(r["SkuID"]),
        })