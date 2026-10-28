
import csv
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "raw"
GROUND_TRUTH_DIR = BASE_DIR / "data" / "ground_truth"

OVERLAP_ID = "EVT-ANOMALY-OVERLAP-000001"
SCRAP_ID = "CNT-ANOMALY-SCRAP-000001"


def read_csv(path):
    with path.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        fields = reader.fieldnames
        rows = list(reader)
    if not fields:
        raise ValueError(f"Missing CSV header: {path}")
    return fields, rows


def write_csv(path, fields, rows):
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def add_label(labels, label):
    label_id = label["anomaly_id"]
    if not any(item.get("anomaly_id") == label_id for item in labels):
        labels.append(label)


def main():
    events_path = DATA_DIR / "state_events.csv"
    counts_path = DATA_DIR / "production_counts.csv"
    truth_path = GROUND_TRUTH_DIR / "ground_truth.json"

    event_fields, events = read_csv(events_path)
    count_fields, counts = read_csv(counts_path)

    required_event_fields = {
        "event_id", "machine_id", "state", "start_time", "end_time"
    }
    required_count_fields = {
        "count_id", "order_id", "machine_id", "product_id",
        "shift_id", "reading_time", "good_count", "scrap_count",
        "total_count", "correction_event"
    }

    if not required_event_fields.issubset(event_fields):
        raise ValueError("state_events.csv is missing required columns.")
    if not required_count_fields.issubset(count_fields):
        raise ValueError("production_counts.csv is missing required columns.")
    if not events or not counts:
        raise ValueError("State events and production counts must not be empty.")

    # Add the overlap anomaly only if it is not already present.
    if not any(row["event_id"] == OVERLAP_ID for row in events):
        source = events[0]
        events.append({
            "event_id": OVERLAP_ID,
            "machine_id": source["machine_id"],
            "state": "STOPPED",
            "start_time": source["start_time"],
            "end_time": source["end_time"],
        })

    # Add the invalid scrap record only if it is not already present.
    if not any(row["count_id"] == SCRAP_ID for row in counts):
        source = counts[0]
        counts.append({
            "count_id": SCRAP_ID,
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

    write_csv(events_path, event_fields, events)
    write_csv(counts_path, count_fields, counts)

    GROUND_TRUTH_DIR.mkdir(parents=True, exist_ok=True)
    if truth_path.exists():
        labels = json.loads(truth_path.read_text(encoding="utf-8"))
    else:
        labels = []

    if not isinstance(labels, list):
        raise ValueError("ground_truth.json must contain a JSON list.")

    add_label(labels, {
        "anomaly_id": "GT-001",
        "issue_type": "OVERLAPPING_MACHINE_STATES",
        "record_id": OVERLAP_ID,
        "expected_decision": "FLAG_OVERLAP",
    })
    add_label(labels, {
        "anomaly_id": "GT-002",
        "issue_type": "SCRAP_EXCEEDS_TOTAL",
        "record_id": SCRAP_ID,
        "expected_decision": "FLAG_INVALID_COUNT",
    })
    add_label(labels, {
        "anomaly_id": "GT-003",
        "issue_type": "COUNT_DECREASE_WITHOUT_CORRECTION",
        "record_id": "CNT-ANOMALY-DECREASE-000002",
        "expected_decision": "FLAG_COUNT_DECREASE",
    })

    truth_path.write_text(json.dumps(labels, indent=2), encoding="utf-8")

    print("Overlap anomaly present:", any(
        row["event_id"] == OVERLAP_ID for row in events
    ))
    print("Scrap anomaly present:", any(
        row["count_id"] == SCRAP_ID for row in counts
    ))
    print("State event rows:", len(events))
    print("Production count rows:", len(counts))
    print("Ground-truth labels:", len(labels))


if __name__ == "__main__":
    main()
