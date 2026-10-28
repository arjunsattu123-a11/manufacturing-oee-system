
import csv
from pathlib import Path

data_dir = Path("data") / "raw"

files = [
    "plants.csv",
    "lines.csv",
    "machines.csv",
    "products.csv",
    "shifts.csv",
    "production_orders.csv",
    "state_events.csv",
    "production_counts.csv",
    "quality_inspections.csv",
    "planned_breaks.csv",
]

for filename in files:
    path = data_dir / filename

    if not path.exists():
        print(f"{filename}: FILE NOT FOUND")
        continue

    with path.open("r", encoding="utf-8", newline="") as file:
        count = sum(1 for _ in csv.DictReader(file))

    print(f"{filename}: {count:,} rows")
