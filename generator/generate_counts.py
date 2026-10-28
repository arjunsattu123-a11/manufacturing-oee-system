
import argparse
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

SEED = 20261022
RECORDS_PER_ORDER = 500
DEFAULT_DATA_DIR = Path("data/raw")


def read_csv(data_dir, filename):
    with (data_dir / filename).open(
        "r", newline="", encoding="utf-8"
    ) as file:
        return list(csv.DictReader(file))


def generate_counts(data_dir):
    rng = random.Random(SEED)

    orders = read_csv(data_dir, "production_orders.csv")
    shifts = read_csv(data_dir, "shifts.csv")
    products = read_csv(data_dir, "products.csv")

    if not orders or not shifts or not products:
        raise ValueError("Orders, shifts, and products must exist.")

    product_ids = {product["product_id"] for product in products}
    shift_windows = []

    for shift in shifts:
        start = datetime.fromisoformat(shift["start_time"])
        shift_windows.append({
            "shift_id": shift["shift_id"],
            "start": start,
            "end": start + timedelta(hours=8),
        })

    counts = []
    count_number = 0

    for order in orders:
        order_id = order["order_id"]
        machine_id = order["machine_id"]
        product_id = order["product_id"]

        if product_id not in product_ids:
            raise ValueError(f"Unknown product in order {order_id}")

        for _ in range(RECORDS_PER_ORDER):
            count_number += 1
            shift = rng.choice(shift_windows)
            duration = int((shift["end"] - shift["start"]).total_seconds())
            reading_time = shift["start"] + timedelta(
                seconds=rng.randrange(duration)
            )

            good_count = rng.randint(1, 20)
            scrap_count = rng.randint(0, 2)

            counts.append({
                "count_id": f"CNT-{order_id}-{count_number:06d}",
                "order_id": order_id,
                "machine_id": machine_id,
                "product_id": product_id,
                "shift_id": shift["shift_id"],
                "reading_time": reading_time.isoformat(),
                "good_count": good_count,
                "scrap_count": scrap_count,
                "total_count": good_count + scrap_count,
                "correction_event": False,
            })

    output_file = data_dir / "production_counts.csv"
    fields = [
        "count_id", "order_id", "machine_id", "product_id",
        "shift_id", "reading_time", "good_count", "scrap_count",
        "total_count", "correction_event",
    ]

    with output_file.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(counts)

    print(f"Production count records: {len(counts)}")
    print(f"Random seed: {SEED}")
    print(f"Saved to: {output_file.resolve()}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data-dir",
        default=str(DEFAULT_DATA_DIR),
        help="Folder containing input CSVs and receiving production_counts.csv",
    )
    args = parser.parse_args()
    generate_counts(Path(args.data_dir))


if __name__ == "__main__":
    main()
