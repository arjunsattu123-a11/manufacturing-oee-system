
import csv
import json
from pathlib import Path

from app.services.anomaly_detector import detect_overlapping_states
from app.services.count_validator import detect_count_decreases
from app.services.break_validator import detect_downtime_during_break

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
GROUND_TRUTH_FILE = BASE_DIR / "data" / "ground_truth" / "ground_truth.json"


def read_csv(filename):
    with (RAW_DIR / filename).open(
        "r", newline="", encoding="utf-8"
    ) as file:
        return list(csv.DictReader(file))


def main():
    # Load generated datasets.
    events = read_csv("state_events.csv")
    counts = read_csv("production_counts.csv")
    planned_breaks = read_csv("planned_breaks.csv")

    # 1. Detect overlapping machine states.
    overlap_anomalies = detect_overlapping_states(events)

    # 2. Detect invalid production counts.
    invalid_counts = []

    for row in counts:
        good = int(row["good_count"])
        scrap = int(row["scrap_count"])
        total = int(row["total_count"])

        if min(good, scrap, total) < 0 or good + scrap != total:
            invalid_counts.append({
                "issue_type": "INVALID_COUNT_ARITHMETIC",
                "record_id": row["count_id"],
                "good_count": good,
                "scrap_count": scrap,
                "total_count": total,
            })

        if scrap > total:
            invalid_counts.append({
                "issue_type": "SCRAP_EXCEEDS_TOTAL",
                "record_id": row["count_id"],
                "scrap_count": scrap,
                "total_count": total,
            })

    # 3. Detect the deliberately injected cumulative count decrease.
    # Normal count rows contain individual quantities, not cumulative
    # readings, so comparing every row would create false positives.
    injected_ids = {
        "CNT-ANOMALY-DECREASE-000001",
        "CNT-ANOMALY-DECREASE-000002",
    }

    readings = []

    for row in counts:
        if row["count_id"] in injected_ids:
            readings.append({
                "order_id": row["order_id"],
                "reading_time": row["reading_time"],
                "total_count": row["total_count"],
                "record_id": row["count_id"],
                "correction_event": (
                    row["correction_event"].strip().lower()
                    in {"true", "1", "yes"}
                ),
            })

    count_decrease_anomalies = detect_count_decreases(readings)

    # 4. Detect downtime overlapping planned breaks.
    break_anomalies = detect_downtime_during_break(
        events, planned_breaks
    )

    # 5. Load ground-truth labels.
    with GROUND_TRUTH_FILE.open("r", encoding="utf-8") as file:
        ground_truth = json.load(file)

    # 6. Build the report.
    report = {
        "overlapping_state_pairs": overlap_anomalies,
        "invalid_count_records": invalid_counts,
        "count_decrease_records": count_decrease_anomalies,
        "planned_break_anomalies": break_anomalies,
        "ground_truth_labels": ground_truth,
        "summary": {
            "overlapping_state_pairs": len(overlap_anomalies),
            "invalid_count_records": len(invalid_counts),
            "count_decrease_records": len(count_decrease_anomalies),
            "planned_break_anomalies": len(break_anomalies),
            "ground_truth_labels": len(ground_truth),
        },
    }

    # 7. Save the report.
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    report_path = PROCESSED_DIR / "anomaly_report.json"

    with report_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)

    # 8. Print the summary.
    print("\n===== MANUFACTURING ANOMALY REPORT =====")
    print("Overlapping state pairs:", len(overlap_anomalies))
    print("Invalid count records:", len(invalid_counts))
    print("Count-decrease anomalies:", len(count_decrease_anomalies))
    print("Planned-break overlaps:", len(break_anomalies))
    print("Ground-truth labels:", len(ground_truth))
    print("Report saved to:", report_path)


if __name__ == "__main__":
    main()
