
from app.services.anomaly_detector import detect_overlapping_states
from app.services.count_validator import detect_count_decreases


def test_detects_overlapping_states():
    events = [
        {
            "event_id": "EVT-M001-000001",
            "machine_id": "M001",
            "state": "RUNNING",
            "start_time": "2026-01-01T10:00:00",
            "end_time": "2026-01-01T10:30:00",
        },
        {
            "event_id": "EVT-M001-000002",
            "machine_id": "M001",
            "state": "STOPPED",
            "start_time": "2026-01-01T10:20:00",
            "end_time": "2026-01-01T10:40:00",
        },
    ]

    anomalies = detect_overlapping_states(events)

    assert len(anomalies) == 1
    assert anomalies[0]["issue_type"] == "OVERLAPPING_MACHINE_STATES"
    assert anomalies[0]["overlap_seconds"] == 600


def test_events_without_overlap():
    events = [
        {
            "event_id": "EVT-M001-000001",
            "machine_id": "M001",
            "state": "RUNNING",
            "start_time": "2026-01-01T10:00:00",
            "end_time": "2026-01-01T10:20:00",
        },
        {
            "event_id": "EVT-M001-000002",
            "machine_id": "M001",
            "state": "STOPPED",
            "start_time": "2026-01-01T10:20:00",
            "end_time": "2026-01-01T10:30:00",
        },
    ]

    assert detect_overlapping_states(events) == []


def test_detects_count_decrease_without_correction():
    readings = [
        {
            "order_id": "PO-001",
            "reading_time": "2026-01-01T10:00:00",
            "total_count": 105,
            "record_id": "READ-001",
            "correction_event": False,
        },
        {
            "order_id": "PO-001",
            "reading_time": "2026-01-01T10:05:00",
            "total_count": 95,
            "record_id": "READ-002",
            "correction_event": False,
        },
    ]

    anomalies = detect_count_decreases(readings)

    assert len(anomalies) == 1
    assert anomalies[0]["issue_type"] == "COUNT_DECREASE_WITHOUT_CORRECTION"
    assert anomalies[0]["previous_count"] == 105
    assert anomalies[0]["current_count"] == 95
