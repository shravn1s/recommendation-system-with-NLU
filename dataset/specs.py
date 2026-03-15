import csv

SPEC_BY_SKU = {}

with open("dataset/spec_mode.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        sku = row.get("SkuID")
        spec = row.get("Spec Mode")

        if sku:
            SPEC_BY_SKU[sku] = spec