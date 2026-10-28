
import csv
import hashlib
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
OUTPUT_DIR = BASE_DIR / "data" / "processed"

FILES_TO_CHECK = [
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


def file_sha256(path):
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def count_csv_rows(path):
    with path.open("r", newline="", encoding="utf-8") as file:
        return sum(1 for _ in csv.DictReader(file))


def main():
    results = {}

    for filename in FILES_TO_CHECK:
        path = RAW_DIR / filename

        if not path.exists():
            results[filename] = {
                "exists": False,
                "rows": None,
                "sha256": None,
            }
            print(f"MISSING: {filename}")
            continue

        rows = count_csv_rows(path)
        checksum = file_sha256(path)

        results[filename] = {
            "exists": True,
            "rows": rows,
            "sha256": checksum,
        }

        print(f"{filename}: {rows:,} rows")
        print(f"  SHA-256: {checksum}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "reproducibility_manifest.json"

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(results, file, indent=2)

    print("\nManifest saved to:", output_path)


if __name__ == "__main__":
    main()
