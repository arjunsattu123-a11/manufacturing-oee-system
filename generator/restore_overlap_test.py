
import argparse
import csv
import json
from pathlib import Path

ANOMALY_ID = "EVT-ANOMALY-OVERLAP-000001"
LABEL_ID = "GT-001"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--truth-file", required=True)
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    truth_file = Path(args.truth_file)
    events_file = data_dir / "state_events.csv"

    with events_file.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames
        events = list(reader)

    if not fieldnames or not events:
        raise ValueError("State events file is empty or missing its header.")

    existing = any(event["event_id"] == ANOMALY_ID for event in events)

    if not existing:
        source = events[0]
        events.append({
            "event_id": ANOMALY_ID,
            "machine_id": source["machine_id"],
            "state": "STOPPED",
            "start_time": source["start_time"],
            "end_time": source["end_time"],
        })

        with events_file.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(events)

    truth_file.parent.mkdir(parents=True, exist_ok=True)

    if truth_file.exists():
        labels = json.loads(truth_file.read_text(encoding="utf-8"))
    else:
        labels = []

    if not isinstance(labels, list):
        raise ValueError("Ground truth must be a JSON list.")

    if not any(label.get("record_id") == ANOMALY_ID for label in labels):
        labels.append({
            "label_id": LABEL_ID,
            "issue_type": "OVERLAPPING_MACHINE_STATES",
            "expected_detection": "FLAG_OVERLAP",
            "record_id": ANOMALY_ID,
        })

    truth_file.write_text(json.dumps(labels, indent=2), encoding="utf-8")

    print("Overlap anomaly present:", True)
    print("State event rows:", len(events))
    print("Ground-truth labels:", len(labels))
    print("Data folder:", data_dir.resolve())
    print("Ground-truth file:", truth_file.resolve())


if __name__ == "__main__":
    main()
