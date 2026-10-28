
import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"

SHIFTS_FILE = RAW_DIR / "shifts.csv"
OUTPUT_FILE = RAW_DIR / "planned_breaks.csv"


def main():
    breaks = []

    with open(SHIFTS_FILE, "r", newline="", encoding="utf-8") as file:
        shifts = list(csv.DictReader(file))

    for shift in shifts:
        shift_id = shift.get("shift_id")
        start_value = shift.get("start_time")

        if not shift_id or not start_value:
            continue

        # This dataset currently uses a 15-minute planned break
        # two hours after the shift start.
        from datetime import datetime, timedelta

        start = datetime.fromisoformat(start_value)
        break_start = start + timedelta(hours=2)
        break_end = break_start + timedelta(minutes=15)

        breaks.append({
            "break_id": f"BRK-{shift_id}",
            "shift_id": shift_id,
            "start_time": break_start.isoformat(),
            "end_time": break_end.isoformat(),
        })

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "break_id",
                "shift_id",
                "start_time",
                "end_time",
            ],
        )
        writer.writeheader()
        writer.writerows(breaks)

    print(f"Created {len(breaks)} planned breaks.")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

import argparse
import csv
from datetime import datetime, timedelta
from pathlib import Path

DEFAULT_DATA_DIR = Path("data/raw")


def generate_breaks(data_dir):
    shifts_file = data_dir / "shifts.csv"
    output_file = data_dir / "planned_breaks.csv"

    with shifts_file.open(
        "r", newline="", encoding="utf-8"
    ) as file:
        shifts = list(csv.DictReader(file))

    breaks = []

    for shift in shifts:
        shift_id = shift.get("shift_id")
        start_value = shift.get("start_time")

        if not shift_id or not start_value:
            continue

        start = datetime.fromisoformat(start_value)
        break_start = start + timedelta(hours=2)
        break_end = break_start + timedelta(minutes=15)

        breaks.append({
            "break_id": f"BRK-{shift_id}",
            "shift_id": shift_id,
            "start_time": break_start.isoformat(),
            "end_time": break_end.isoformat(),
        })

    fields = ["break_id", "shift_id", "start_time", "end_time"]

    with output_file.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(breaks)

    print(f"Created {len(breaks)} planned breaks.")
    print(f"Saved to: {output_file.resolve()}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data-dir",
        default=str(DEFAULT_DATA_DIR),
        help="Folder containing shifts.csv and receiving planned_breaks.csv",
    )
    args = parser.parse_args()
    generate_breaks(Path(args.data_dir))


if __name__ == "__main__":
    main()
