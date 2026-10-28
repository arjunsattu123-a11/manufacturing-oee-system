def detect_invalid_cycle_times(products: list[dict]) -> list[dict]:
    anomalies = []

    for product in products:
        try:
            cycle_time = float(product["ideal_cycle_time_seconds"])
        except (KeyError, TypeError, ValueError):
            cycle_time = 0

        if cycle_time <= 0:
            anomalies.append({
                "issue_type": "INVALID_IDEAL_CYCLE_TIME",
                "product_id": product.get("product_id"),
                "ideal_cycle_time_seconds": product.get(
                    "ideal_cycle_time_seconds"
                ),
                "expected_decision": "FLAG_INVALID_CYCLE_TIME",
            })

    return anomalies
