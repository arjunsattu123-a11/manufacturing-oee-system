
import pytest

from app.services.oee_calculator import calculate_oee


def test_calculates_oee():
    result = calculate_oee(
        planned_time_seconds=3600,
        run_time_seconds=3000,
        ideal_cycle_time_seconds=2,
        total_count=1200,
        good_count=1140,
    )

    assert result["availability"] == 0.8333
    assert result["performance"] == 0.8
    assert result["quality"] == 0.95
    assert result["oee"] == 0.6333


def test_rejects_invalid_planned_time():
    with pytest.raises(ValueError):
        calculate_oee(0, 0, 2, 100, 90)


def test_rejects_good_count_above_total():
    with pytest.raises(ValueError):
        calculate_oee(3600, 3000, 2, 100, 120)
