
import csv
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
GROUND_TRUTH_FILE = (
    BASE_DIR / "data" / "ground_truth" / "ground_truth.json"
)

ANOMALY_ID = "EVT-ANOMALY-OVERLAP-000001"
LABEL_ID = "GT-001"


def main():
    events_file = RAW_DIR / "state_events.csv"

    # Load the existing state events.
    with events_file.open(
        "r", newline="", encoding="utf-8"
    ) as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames
        events = list(reader)

    if not fieldnames:
        raise ValueError("state_events.csv has no header.")

    required_fields = {
        "event_id",
        "machine_id",
        "state",
        "start_time",
        "end_time",
    }

    if not required_fields.issubset(fieldnames):
        raise ValueError(
            f"Missing required columns: {required_fields - set(fieldnames)}"
        )

    # If this anomaly already exists, don't add it again.
    existing = next(
        (event for event in events if event["event_id"] == ANOMALY_ID),
        None,
    )

    if existing:
        print("Overlap anomaly already exists; no duplicate added.")
    else:
        if not events:
            raise ValueError("No events found in state_events.csv.")

        # Use the first real event, regardless of machine ID.
        source = events[0]

        # Same interval on the same machine guarantees an overlap.
        anomaly = {
            "event_id": ANOMALY_ID,
            "machine_id": source["machine_id"],
            "state": "STOPPED",
            "start_time": source["start_time"],
            "end_time": source["end_time"],
        }

        events.append(anomaly)

        with events_file.open(
            "w", newline="", encoding="utf-8"
        ) as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(events)

        print("Restored one labelled overlapping-state anomaly.")
        print(f"State events now: {len(events)}")

    # Load existing ground-truth labels.
    GROUND_TRUTH_FILE.parent.mkdir(
        parents=True, exist_ok=True
    )

    if GROUND_TRUTH_FILE.exists():
        with GROUND_TRUTH_FILE.open(
            "r", encoding="utf-8"
        ) as file:
            labels = json.load(file)
    else:
        labels = []

    if not isinstance(labels, list):
        raise ValueError(
            "Expected ground_truth.json to contain a JSON list."
        )

    # Preserve existing labels and avoid duplicate labels.
    label_exists = any(
        label.get("record_id") == ANOMALY_ID
        for label in labels
    )

    if not label_exists:
        labels.append({
            "label_id": LABEL_ID,
            "issue_type": "OVERLAPPING_MACHINE_STATES",
            "expected_detection": "FLAG_OVERLAP",
            "record_id": ANOMALY_ID,
        })

        with GROUND_TRUTH_FILE.open(
            "w", encoding="utf-8"
        ) as file:
            json.dump(labels, file, indent=2)

        print("Ground-truth overlap label added.")
    else:
        print("Ground-truth overlap label already exists.")

    print(f"Ground-truth labels: {len(labels)}")


if __name__ == "__main__":
    main()
