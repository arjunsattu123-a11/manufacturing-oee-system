
import csv
import json
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "raw"
GROUND_TRUTH_DIR = BASE_DIR / "data" / "ground_truth"

ANOMALIES = [
    {
        "count_id": "CNT-ANOMALY-DECREASE-000001",
        "good_count": 100,
        "scrap_count": 5,
        "total_count": 105,
        "minutes": 0,
    },
    {
        "count_id": "CNT-ANOMALY-DECREASE-000002",
        "good_count": 90,
        "scrap_count": 5,
        "total_count": 95,
        "minutes": 5,
    },
]


def main():
    counts_file = DATA_DIR / "production_counts.csv"

    with counts_file.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames
        counts = list(reader)

    if not fieldnames or not counts:
        raise ValueError("Production counts CSV is empty or has no header.")

    required = {
        "count_id", "order_id", "machine_id", "product_id",
        "shift_id", "reading_time", "good_count", "scrap_count",
        "total_count", "correction_event",
    }
    missing = required - set(fieldnames)
    if missing:
        raise ValueError(f"Missing columns in production_counts.csv: {missing}")

    existing_ids = {row["count_id"] for row in counts}
    first_count = counts[0]

    # Keep the two example readings close together in time.
    first_time = datetime.fromisoformat(first_count["reading_time"])

    new_rows = []
    for anomaly in ANOMALIES:
        if anomaly["count_id"] in existing_ids:
            print(f"Already exists: {anomaly['count_id']}")
            continue

        row = {
            "count_id": anomaly["count_id"],
            "order_id": first_count["order_id"],
            "machine_id": first_count["machine_id"],
            "product_id": first_count["product_id"],
            "shift_id": first_count["shift_id"],
            "reading_time": (
                first_time + timedelta(minutes=anomaly["minutes"])
            ).isoformat(),
            "good_count": str(anomaly["good_count"]),
            "scrap_count": str(anomaly["scrap_count"]),
            "total_count": str(anomaly["total_count"]),
            "correction_event": "False",
        }
        new_rows.append(row)
        existing_ids.add(anomaly["count_id"])

    counts.extend(new_rows)

    with counts_file.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(counts)

    GROUND_TRUTH_DIR.mkdir(parents=True, exist_ok=True)
    truth_file = GROUND_TRUTH_DIR / "ground_truth.json"

    if truth_file.exists():
        truth = json.loads(truth_file.read_text(encoding="utf-8"))
    else:
        truth = []

    # Support either label key used by earlier project scripts.
    already_labelled = any(
        label.get("record_id") == "CNT-ANOMALY-DECREASE-000002"
        or label.get("anomaly_id") == "GT-003"
        or label.get("label_id") == "GT-003"
        for label in truth
    )

    if not already_labelled:
        truth.append({
            "anomaly_id": "GT-003",
            "issue_type": "COUNT_DECREASE_WITHOUT_CORRECTION",
            "record_id": "CNT-ANOMALY-DECREASE-000002",
            "expected_decision": "FLAG_COUNT_DECREASE",
        })

    truth_file.write_text(json.dumps(truth, indent=2), encoding="utf-8")

    print("New count anomaly rows added:", len(new_rows))
    print("Total production count rows:", len(counts))
    print("Ground-truth labels:", len(truth))


if __name__ == "__main__":
    main()
