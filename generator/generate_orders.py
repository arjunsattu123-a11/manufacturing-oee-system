
import argparse
import csv
import random
from pathlib import Path

SEED = 20261022
DEFAULT_DATA_DIR = Path("data/raw")


def read_csv(data_dir, filename):
    with (data_dir / filename).open(
        "r", newline="", encoding="utf-8"
    ) as file:
        return list(csv.DictReader(file))


def generate_orders(data_dir, number_of_orders=1000):
    rng = random.Random(SEED)

    machines = read_csv(data_dir, "machines.csv")
    products = read_csv(data_dir, "products.csv")

    if not machines or not products:
        raise ValueError("Machines and products CSV files must not be empty.")

    orders = []

    for i in range(1, number_of_orders + 1):
        machine = rng.choice(machines)
        product = rng.choice(products)

        orders.append({
            "order_id": f"PO-2026-{i:06d}",
            "machine_id": machine["machine_id"],
            "product_id": product["product_id"],
            "planned_quantity": rng.randint(500, 5000),
            "status": "COMPLETED",
        })

    output_file = data_dir / "production_orders.csv"

    with output_file.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=orders[0].keys())
        writer.writeheader()
        writer.writerows(orders)

    print(f"Production orders generated: {len(orders)}")
    print(f"Random seed: {SEED}")
    print(f"Saved to: {output_file.resolve()}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data-dir",
        default=str(DEFAULT_DATA_DIR),
        help="Folder containing input CSVs and receiving production_orders.csv",
    )
    args = parser.parse_args()

    generate_orders(Path(args.data_dir))


if __name__ == "__main__":
    main()
