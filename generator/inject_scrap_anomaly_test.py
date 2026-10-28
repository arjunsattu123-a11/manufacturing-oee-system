
import argparse
import csv
import json
from pathlib import Path

ANOMALY_ID = "CNT-ANOMALY-SCRAP-000001"


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

    if not any(row["count_id"] == ANOMALY_ID for row in counts):
        source = counts[0]
        counts.append({
            "count_id": ANOMALY_ID,
            "order_id": source["order_id"],
            "machine_id": source["machine_id"],
            "product_id": source["product_id"],
            "shift_id": source["shift_id"],
            "reading_time": source["reading_time"],
            "good_count": "10",
            "scrap_count": "20",
            "total_count": "5",
            "correction_event": "False",
        })

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

    if not any(label.get("anomaly_id") == "GT-002" for label in labels):
        labels.append({
            "anomaly_id": "GT-002",
            "issue_type": "SCRAP_EXCEEDS_TOTAL",
            "record_id": ANOMALY_ID,
            "expected_decision": "FLAG_INVALID_COUNT",
        })

    truth_file.write_text(json.dumps(labels, indent=2), encoding="utf-8")

    print("Scrap anomaly present:", True)
    print("Production count rows:", len(counts))
    print("Ground-truth labels:", len(labels))


if __name__ == "__main__":
    main()
