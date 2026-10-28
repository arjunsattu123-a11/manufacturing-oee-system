
import argparse
import csv
import json
from datetime import datetime, timedelta
from pathlib import Path

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
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--truth-file", required=True)
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    truth_file = Path(args.truth_file)
    counts_file = data_dir / "production_counts.csv"

    with counts_file.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        fields = reader.fieldnames
        counts = list(reader)

    if not fields or not counts:
        raise ValueError("Production counts file is empty.")

    existing_ids = {row["count_id"] for row in counts}
    first = counts[0]
    first_time = datetime.fromisoformat(first["reading_time"])

    for anomaly in ANOMALIES:
        if anomaly["count_id"] in existing_ids:
            continue

        counts.append({
            "count_id": anomaly["count_id"],
            "order_id": first["order_id"],
            "machine_id": first["machine_id"],
            "product_id": first["product_id"],
            "shift_id": first["shift_id"],
            "reading_time": (
                first_time + timedelta(minutes=anomaly["minutes"])
            ).isoformat(),
            "good_count": str(anomaly["good_count"]),
            "scrap_count": str(anomaly["scrap_count"]),
            "total_count": str(anomaly["total_count"]),
            "correction_event": "False",
        })
        existing_ids.add(anomaly["count_id"])

    with counts_file.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(counts)

    truth_file.parent.mkdir(parents=True, exist_ok=True)
    if truth_file.exists():
        labels = json.loads(truth_file.read_text(encoding="utf-8"))
    else:
        labels = []

    if not isinstance(labels, list):
        raise ValueError("Ground truth must be a JSON list.")

    if not any(label.get("anomaly_id") == "GT-003" for label in labels):
        labels.append({
            "anomaly_id": "GT-003",
            "issue_type": "COUNT_DECREASE_WITHOUT_CORRECTION",
            "record_id": "CNT-ANOMALY-DECREASE-000002",
            "expected_decision": "FLAG_COUNT_DECREASE",
        })

    truth_file.write_text(json.dumps(labels, indent=2), encoding="utf-8")

    print("Count-decrease anomaly records:", 2)
    print("Production count rows:", len(counts))
    print("Ground-truth labels:", len(labels))


if __name__ == "__main__":
    main()

