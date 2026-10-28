
import argparse
import csv
from pathlib import Path

DEFAULT_DATA_DIR = Path("data/raw")


def generate_quality(data_dir):
    counts_file = data_dir / "production_counts.csv"
    output_file = data_dir / "quality_inspections.csv"

    records = []

    with counts_file.open("r", newline="", encoding="utf-8") as file:
        counts = csv.DictReader(file)

        for index, count in enumerate(counts, start=1):
            good = int(count["good_count"])
            scrap = int(count["scrap_count"])
            total = int(count["total_count"])

            if good + scrap != total:
                raise ValueError(
                    f"Invalid count arithmetic: {count['count_id']}"
                )

            records.append({
                "inspection_id": (
                    f"QC-{count['order_id']}-{index:06d}"
                ),
                "order_id": count["order_id"],
                "inspected_quantity": total,
                "rejected_quantity": scrap,
                "passed_quantity": good,
            })

    with output_file.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "inspection_id",
                "order_id",
                "inspected_quantity",
                "rejected_quantity",
                "passed_quantity",
            ],
        )
        writer.writeheader()
        writer.writerows(records)

    print(f"Quality inspection records: {len(records)}")
    print(f"Saved to: {output_file.resolve()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DEFAULT_DATA_DIR,
    )
    args = parser.parse_args()

    generate_quality(args.data_dir)
