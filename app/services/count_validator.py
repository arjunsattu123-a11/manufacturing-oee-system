
def detect_count_decreases(readings: list[dict]) -> list[dict]:
    """
    Detect decreases in cumulative production readings.
    Readings must contain order_id, reading_time,
    total_count, and correction_event.
    """
    anomalies = []
    grouped = {}

    for reading in readings:
        grouped.setdefault(reading["order_id"], []).append(reading)

    for order_id, records in grouped.items():
        records.sort(key=lambda r: r["reading_time"])

        previous = None

        for current in records:
            current_count = int(current["total_count"])

            if previous is not None:
                previous_count = int(previous["total_count"])

                if current_count < previous_count:
                    if not current.get("correction_event", False):
                        anomalies.append({
                            "issue_type": "COUNT_DECREASE_WITHOUT_CORRECTION",
                            "order_id": order_id,
                            "record_id": current["record_id"],
                            "previous_count": previous_count,
                            "current_count": current_count,
                            "reason": (
                                "Cumulative count decreased without "
                                "a correction event."
                            ),
                        })

            previous = current

    return anomalies
