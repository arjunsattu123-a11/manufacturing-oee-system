
from datetime import datetime


def detect_downtime_during_break(
    state_events: list[dict],
    planned_breaks: list[dict],
) -> list[dict]:
    anomalies = []

    for planned_break in planned_breaks:
        break_start = datetime.fromisoformat(
            planned_break["start_time"]
        )
        break_end = datetime.fromisoformat(
            planned_break["end_time"]
        )

        if break_end <= break_start:
            continue

        for event in state_events:
            if event["state"].upper() not in {"STOPPED", "IDLE"}:
                continue

            event_start = datetime.fromisoformat(event["start_time"])
            event_end = datetime.fromisoformat(event["end_time"])

            if event_end <= event_start:
                continue

            overlap_start = max(event_start, break_start)
            overlap_end = min(event_end, break_end)

            if overlap_start < overlap_end:
                anomalies.append({
                    "issue_type": "DOWNTIME_OVERLAPS_PLANNED_BREAK",
                    "event_id": event["event_id"],
                    "machine_id": event["machine_id"],
                    "break_id": planned_break["break_id"],
                    "shift_id": planned_break.get("shift_id"),
                    "overlap_start": overlap_start.isoformat(),
                    "overlap_end": overlap_end.isoformat(),
                    "overlap_seconds": int(
                        (overlap_end - overlap_start).total_seconds()
                    ),
                })

    return anomalies
