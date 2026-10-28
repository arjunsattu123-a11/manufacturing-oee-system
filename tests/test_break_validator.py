
from app.services.break_validator import detect_downtime_during_break


def test_detects_downtime_overlapping_planned_break():
    events = [{
        "event_id": "EVT-001",
        "machine_id": "M001",
        "state": "STOPPED",
        "start_time": "2026-01-01T10:10:00",
        "end_time": "2026-01-01T10:30:00",
    }]

    planned_breaks = [{
        "break_id": "BRK-001",
        "start_time": "2026-01-01T10:20:00",
        "end_time": "2026-01-01T10:40:00",
    }]

    anomalies = detect_downtime_during_break(events, planned_breaks)

    assert len(anomalies) == 1
    assert anomalies[0]["issue_type"] == (
        "DOWNTIME_OVERLAPS_PLANNED_BREAK"
    )
    assert anomalies[0]["overlap_seconds"] == 600


def test_no_anomaly_when_downtime_is_outside_break():
    events = [{
        "event_id": "EVT-002",
        "machine_id": "M001",
        "state": "STOPPED",
        "start_time": "2026-01-01T09:00:00",
        "end_time": "2026-01-01T09:10:00",
    }]

    planned_breaks = [{
        "break_id": "BRK-001",
        "start_time": "2026-01-01T10:00:00",
        "end_time": "2026-01-01T10:20:00",
    }]

    assert detect_downtime_during_break(events, planned_breaks) == []
