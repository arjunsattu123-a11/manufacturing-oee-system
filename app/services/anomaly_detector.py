
from datetime import datetime


def detect_overlapping_states(events: list[dict]) -> list[dict]:
    anomalies = []
    machine_events = {}

    for event in events:
        machine_id = event["machine_id"]
        machine_events.setdefault(machine_id, []).append(event)

    for machine_id, records in machine_events.items():
        records = sorted(
            records,
            key=lambda event: event["start_time"],
        )

        for i, first in enumerate(records):
            first_start = datetime.fromisoformat(first["start_time"])
            first_end = datetime.fromisoformat(first["end_time"])

            if first_start >= first_end:
                anomalies.append({
                    "issue_type": "INVALID_STATE_INTERVAL",
                    "machine_id": machine_id,
                    "event_ids": [first["event_id"]],
                    "reason": "Start time must be earlier than end time.",
                })
                continue

            for second in records[i + 1:]:
                second_start = datetime.fromisoformat(second["start_time"])
                second_end = datetime.fromisoformat(second["end_time"])

                if second_start >= first_end:
                    break

                if second_start >= second_end:
                    anomalies.append({
                        "issue_type": "INVALID_STATE_INTERVAL",
                        "machine_id": machine_id,
                        "event_ids": [second["event_id"]],
                        "reason": "Start time must be earlier than end time.",
                    })
                    continue

                overlap_start = max(first_start, second_start)
                overlap_end = min(first_end, second_end)

                if overlap_start < overlap_end:
                    anomalies.append({
                        "issue_type": "OVERLAPPING_MACHINE_STATES",
                        "machine_id": machine_id,
                        "event_ids": [
                            first["event_id"],
                            second["event_id"],
                        ],
                        "overlap_start": overlap_start.isoformat(),
                        "overlap_end": overlap_end.isoformat(),
                        "overlap_seconds": (
                            overlap_end - overlap_start
                        ).total_seconds(),
                        "reason": "Two machine-state events overlap in time.",
                    })

    return anomalies
