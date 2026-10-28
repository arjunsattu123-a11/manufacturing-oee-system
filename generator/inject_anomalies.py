
import csv
import json
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "raw"
GROUND_TRUTH_DIR = BASE_DIR / "data" / "ground_truth"

OVERLAP_ID = "EVT-ANOMALY-OVERLAP-000001"
SCRAP_ID = "CNT-ANOMALY-SCRAP-000001"
BREAK_EVENT_ID = "EVT-ANOMALY-BREAK-000001"


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
    for existing in labels:
        if existing.get("anomaly_id") == label["anomaly_id"]:
            existing.update(label)
            return
    labels.append(label)


def find_free_interval(events, machine_id, break_start, break_end):
    """Find a free 15-minute interval inside a planned break."""
    duration = timedelta(minutes=15)
    intervals = []

    for event in events:
        if event["machine_id"] != machine_id:
            continue

        start = datetime.fromisoformat(event["start_time"])
        end = datetime.fromisoformat(event["end_time"])

        if end > break_start and start < break_end:
            intervals.append((start, end))

    intervals.sort()
    candidate = break_start

    for start, end in intervals:
        if start - candidate >= duration:
            return candidate, candidate + duration

        if end > candidate:
            candidate = end

    if break_end - candidate >= duration:
        return candidate, candidate + duration

    return None


def main():
    events_path = DATA_DIR / "state_events.csv"
    counts_path = DATA_DIR / "production_counts.csv"
    breaks_path = DATA_DIR / "planned_breaks.csv"
    truth_path = GROUND_TRUTH_DIR / "ground_truth.json"

    event_fields, events = read_csv(events_path)
    count_fields, counts = read_csv(counts_path)
    _, breaks = read_csv(breaks_path)

    # 1. Inject one overlapping machine-state anomaly.
    if not any(e["event_id"] == OVERLAP_ID for e in events):
        source = next(
            e for e in events
            if e["machine_id"] == "M-001"
        )
        events.append({
            "event_id": OVERLAP_ID,
            "machine_id": source["machine_id"],
            "state": "STOPPED",
            "start_time": source["start_time"],
            "end_time": source["end_time"],
        })

    # 2. Inject scrap exceeding total count.
    if not any(c["count_id"] == SCRAP_ID for c in counts):
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

    # 3. Ensure the break anomaly exists and overlaps a planned break.
    # If it already exists, preserve its current position.
    break_event = next(
        (e for e in events if e["event_id"] == BREAK_EVENT_ID),
        None,
    )

    if break_event is None:
        placed = False

        machine_ids = sorted({
            e["machine_id"] for e in events
            if e["event_id"] != OVERLAP_ID
        })

        for planned_break in breaks:
            break_start = datetime.fromisoformat(
                planned_break["start_time"]
            )
            break_end = datetime.fromisoformat(
                planned_break["end_time"]
            )

            if break_end <= break_start:
                continue

            for machine_id in machine_ids:
                interval = find_free_interval(
                    events, machine_id, break_start, break_end
                )

                if interval is None:
                    continue

                event_start, event_end = interval

                break_event = {
                    "event_id": BREAK_EVENT_ID,
                    "machine_id": machine_id,
                    "state": "STOPPED",
                    "start_time": event_start.isoformat(),
                    "end_time": event_end.isoformat(),
                }
                events.append(break_event)
                placed = True
                break

            if placed:
                break

        if not placed:
            raise RuntimeError(
                "No conflict-free 15-minute interval found "
                "inside the planned breaks."
            )

    # 4. Save data.
    write_csv(events_path, event_fields, events)
    write_csv(counts_path, count_fields, counts)

    # 5. Preserve and update ground-truth labels.
    GROUND_TRUTH_DIR.mkdir(parents=True, exist_ok=True)

    if truth_path.exists():
        labels = json.loads(
            truth_path.read_text(encoding="utf-8")
        )
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

    add_label(labels, {
        "anomaly_id": "GT-004",
        "issue_type": "DOWNTIME_OVERLAPS_PLANNED_BREAK",
        "record_id": BREAK_EVENT_ID,
        "expected_decision": "FLAG_DOWNTIME_BREAK_OVERLAP",
    })

    truth_path.write_text(
        json.dumps(labels, indent=2),
        encoding="utf-8",
    )

    print("Overlap anomaly present:", any(
        e["event_id"] == OVERLAP_ID for e in events
    ))
    print("Scrap anomaly present:", any(
        c["count_id"] == SCRAP_ID for c in counts
    ))
    print("Break anomaly present:", any(
        e["event_id"] == BREAK_EVENT_ID for e in events
    ))
    print("State event rows:", len(events))
    print("Production count rows:", len(counts))
    print("Ground-truth labels:", len(labels))


if __name__ == "__main__":
    main()
