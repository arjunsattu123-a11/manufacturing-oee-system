
import argparse
import csv
from pathlib import Path
from collections import Counter

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"


def read_csv(filename):
    path = RAW_DIR / filename

    with open(path, "r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def duplicate_ids(rows, id_field):
    values = [row.get(id_field, "") for row in rows]
    counts = Counter(values)

    return [
        value for value, count in counts.items()
        if not value or count > 1
    ]


def invalid_references(rows, field, valid_ids):
    return [
        row for row in rows
        if row.get(field, "") not in valid_ids
    ]


def check_event_times(events):
    invalid_intervals = []
    by_machine = {}

    from datetime import datetime

    for event in events:
        try:
            start = datetime.fromisoformat(event["start_time"])
            end = datetime.fromisoformat(event["end_time"])

            if end <= start:
                invalid_intervals.append(event)
                continue

            by_machine.setdefault(
                event["machine_id"], []
            ).append((start, end, event["event_id"]))

        except (ValueError, KeyError):
            invalid_intervals.append(event)

    overlaps = []

    for machine_id, intervals in by_machine.items():
        intervals.sort(key=lambda item: item[0])

        for i in range(len(intervals)):
            start1, end1, id1 = intervals[i]

            for j in range(i + 1, len(intervals)):
                start2, end2, id2 = intervals[j]

                if start2 >= end1:
                    break

                overlap_start = max(start1, start2)
                overlap_end = min(end1, end2)

                if overlap_start < overlap_end:
                    overlaps.append({
                        "machine_id": machine_id,
                        "event_ids": [id1, id2],
                        "overlap_seconds": int(
                            (overlap_end - overlap_start).total_seconds()
                        ),
                    })

    return invalid_intervals, overlaps


def main():
    print("=== Loading data ===")

    plants = read_csv("plants.csv")
    lines = read_csv("lines.csv")
    machines = read_csv("machines.csv")
    products = read_csv("products.csv")
    orders = read_csv("production_orders.csv")
    events = read_csv("state_events.csv")
    counts = read_csv("production_counts.csv")
    inspections = read_csv("quality_inspections.csv")
    #planned_breaks = read_csv(BREAKS_FILE)

    # 1. Primary key uniqueness
    print("\n=== Primary Key Checks ===")

    pk_checks = [
        ("Plant", plants, "plant_id"),
        ("Line", lines, "line_id"),
        ("Machine", machines, "machine_id"),
        ("Product", products, "product_id"),
        ("Order", orders, "order_id"),
        ("Event", events, "event_id"),
        ("Count", counts, "count_id"),
        ("Inspection", inspections, "inspection_id"),
    ]

    all_primary_keys_unique = True

    for name, rows, field in pk_checks:
        duplicates = duplicate_ids(rows, field)
        passed = len(duplicates) == 0
        all_primary_keys_unique &= passed

        print(
            f"{name}: "
            f"{'PASS' if passed else 'FAIL'} "
            f"({len(duplicates)} duplicate/empty IDs)"
        )

    # 2. Foreign key integrity
    print("\n=== Foreign Key Checks ===")

    plant_ids = {row["plant_id"] for row in plants}
    line_ids = {row["line_id"] for row in lines}
    machine_ids = {row["machine_id"] for row in machines}
    product_ids = {row["product_id"] for row in products}
    order_ids = {row["order_id"] for row in orders}

    fk_checks = [
        ("Line -> Plant", lines, "plant_id", plant_ids),
        ("Machine -> Line", machines, "line_id", line_ids),
        ("Order -> Machine", orders, "machine_id", machine_ids),
        ("Order -> Product", orders, "product_id", product_ids),
        ("Event -> Machine", events, "machine_id", machine_ids),
        ("Count -> Order", counts, "order_id", order_ids),
        ("Inspection -> Order", inspections, "order_id", order_ids),
    ]

    all_foreign_keys_valid = True

    for name, rows, field, valid_ids in fk_checks:
        invalid = invalid_references(rows, field, valid_ids)
        passed = len(invalid) == 0
        all_foreign_keys_valid &= passed

        print(
            f"{name}: "
            f"{'PASS' if passed else 'FAIL'} "
            f"({len(invalid)} invalid references)"
        )

    # 3. Event timestamp and overlap checks
    print("\n=== Event Time Checks ===")

    invalid_intervals, overlaps = check_event_times(events)

    print("Invalid intervals:", len(invalid_intervals))
    print("Overlapping event pairs:", len(overlaps))

    # The challenge intentionally injects one overlap.
    # Verify that the known injected event participates in an overlap.
    expected_event_id = "EVT-ANOMALY-OVERLAP-000001"

    expected_overlap_found = any(
        expected_event_id in overlap["event_ids"]
        for overlap in overlaps
    )

    unexpected_overlaps = [
        overlap for overlap in overlaps
        if expected_event_id not in overlap["event_ids"]
    ]

    print("Expected injected overlap found:", expected_overlap_found)
    print("Unexpected overlapping pairs:", len(unexpected_overlaps))

    # 4. Count arithmetic checks
    print("\n=== Production Count Checks ===")

    invalid_counts = []

    for row in counts:
        try:
            good = int(row["good_count"])
            scrap = int(row["scrap_count"])
            total = int(row["total_count"])

            if good < 0 or scrap < 0 or total < 0:
                invalid_counts.append(row)
            elif good + scrap != total:
                invalid_counts.append(row)

        except (ValueError, KeyError):
            invalid_counts.append(row)

    # One invalid scrap record is intentionally injected.
    expected_invalid_count_id = "CNT-ANOMALY-SCRAP-000001"

    expected_invalid_count_found = any(
        row.get("count_id") == expected_invalid_count_id
        for row in invalid_counts
    )

    unexpected_invalid_counts = [
        row for row in invalid_counts
        if row.get("count_id") != expected_invalid_count_id
    ]

    print("Invalid count arithmetic records:", len(invalid_counts))
    print("Expected injected count anomaly found:",
          expected_invalid_count_found)
    print("Unexpected count arithmetic errors:",
          len(unexpected_invalid_counts))

    # 5. Final summary
    # Intentional anomalies are reported, not mistaken for clean data.
    all_checks_passed = (
        all_primary_keys_unique
        and all_foreign_keys_valid
        and len(invalid_intervals) == 0
        and expected_overlap_found
        and len(unexpected_overlaps) == 0
        and expected_invalid_count_found
        and len(unexpected_invalid_counts) == 0
    )

    print("\n=== Final Summary ===")
    print("All primary keys unique:", all_primary_keys_unique)
    print("All foreign keys valid:", all_foreign_keys_valid)
    print("Event intervals valid:", len(invalid_intervals) == 0)
    print("Expected overlap labelled:", expected_overlap_found)
    print("Expected count anomaly labelled:", expected_invalid_count_found)
    print("No unexpected overlaps:", len(unexpected_overlaps) == 0)
    print("No unexpected count errors:", len(unexpected_invalid_counts) == 0)
    print("All validation checks passed:", all_checks_passed)


if __name__ == "__main__":
    main()
