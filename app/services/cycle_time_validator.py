def detect_invalid_cycle_times(
    products: list[dict],
    expected_products: list[dict] | None = None,
) -> list[dict]:
    anomalies = []

    expected_by_id = {
        row["product_id"]: float(row["ideal_cycle_time_seconds"])
        for row in (expected_products or [])
        if row.get("product_id")
        and row.get("ideal_cycle_time_seconds") not in (None, "")
    }

    for product in products:
        product_id = product.get("product_id")
        raw_value = product.get("ideal_cycle_time_seconds")

        try:
            actual = float(raw_value)
        except (TypeError, ValueError):
            actual = 0

        if actual <= 0:
            anomalies.append({
                "issue_type": "INVALID_IDEAL_CYCLE_TIME",
                "product_id": product_id,
                "ideal_cycle_time_seconds": raw_value,
                "expected_decision": "FLAG_INVALID_CYCLE_TIME",
            })
            continue

        expected = expected_by_id.get(product_id)

        if expected is not None and actual != expected:
            anomalies.append({
                "issue_type": "WRONG_IDEAL_CYCLE_TIME",
                "product_id": product_id,
                "expected_ideal_cycle_time_seconds": expected,
                "actual_ideal_cycle_time_seconds": actual,
                "expected_decision": "FLAG_WRONG_IDEAL_CYCLE_TIME",
            })

    return anomalies
