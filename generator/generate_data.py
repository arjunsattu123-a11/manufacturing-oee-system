
import argparse
import csv
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 20261022
DEFAULT_OUTPUT_DIR = Path("data/raw")


def generate_master_data():
    rng = random.Random(SEED)

    plants = [{"plant_id": "PLANT-001", "name": "Hyderabad Plant"}]

    lines = [
        {"line_id": f"LINE-{i:03d}", "plant_id": "PLANT-001"}
        for i in range(1, 6)
    ]

    machines = [
        {
            "machine_id": f"M-{i:03d}",
            "line_id": f"LINE-{((i - 1) // 6) + 1:03d}",
            "name": f"Machine {i}",
        }
        for i in range(1, 31)
    ]

    products = [
        {
            "product_id": f"PROD-{i:03d}",
            "name": f"Product {i}",
            "ideal_cycle_time_seconds": rng.choice([10, 15, 20, 30]),
        }
        for i in range(1, 21)
    ]

    return plants, lines, machines, products


def generate_shifts(days=90):
    shifts = []
    start_date = date(2026, 1, 1)

    for day_offset in range(days):
        current_date = start_date + timedelta(days=day_offset)

        for shift_code, start_hour in [("A", 6), ("B", 14), ("C", 22)]:
            shifts.append({
                "shift_id": f"SHIFT-{current_date}-{shift_code}",
                "shift_date": str(current_date),
                "shift_code": shift_code,
                "start_time": f"{current_date} {start_hour:02d}:00:00",
            })

    return shifts


def write_csv(output_dir, filename, rows):
    if not rows:
        raise ValueError(f"No rows generated for {filename}")

    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / filename

    with output_file.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"{filename}: {len(rows)} rows")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Folder where generated CSV files will be written",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)

    plants, lines, machines, products = generate_master_data()
    shifts = generate_shifts()

    write_csv(output_dir, "plants.csv", plants)
    write_csv(output_dir, "lines.csv", lines)
    write_csv(output_dir, "machines.csv", machines)
    write_csv(output_dir, "products.csv", products)
    write_csv(output_dir, "shifts.csv", shifts)

    print(f"Random seed: {SEED}")
    print(f"Output folder: {output_dir.resolve()}")


if __name__ == "__main__":
    main()
