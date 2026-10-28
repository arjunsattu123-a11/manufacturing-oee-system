import csv
import json
from pathlib import Path

base = Path(__file__).resolve().parent.parent
products_path = base / "data" / "raw" / "products.csv"
truth_path = base / "data" / "ground_truth" / "ground_truth.json"

with products_path.open("r", newline="", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    fields = reader.fieldnames
    products = list(reader)

product = next((p for p in products if p["product_id"] == "PROD-001"), None)
if product is None:
    raise SystemExit("PROD-001 not found.")

if product["ideal_cycle_time_seconds"] == "20":
    product["ideal_cycle_time_seconds"] = "30"
elif product["ideal_cycle_time_seconds"] != "30":
    raise SystemExit("Unexpected cycle time; inspect products.csv before changing it.")

with products_path.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(products)

labels = json.loads(truth_path.read_text(encoding="utf-8")) if truth_path.exists() else []
label = {
    "anomaly_id": "GT-005",
    "issue_type": "WRONG_IDEAL_CYCLE_TIME",
    "record_id": "PROD-001",
    "expected_ideal_cycle_time_seconds": 20,
    "actual_ideal_cycle_time_seconds": 30,
    "expected_decision": "FLAG_WRONG_IDEAL_CYCLE_TIME"
}
for i, existing in enumerate(labels):
    if existing.get("anomaly_id") == "GT-005":
        labels[i] = label
        break
else:
    labels.append(label)

truth_path.parent.mkdir(parents=True, exist_ok=True)
truth_path.write_text(json.dumps(labels, indent=2), encoding="utf-8")

print("Product:", product["product_id"])
print("Injected cycle time:", product["ideal_cycle_time_seconds"])
print("Ground-truth labels:", len(labels))
