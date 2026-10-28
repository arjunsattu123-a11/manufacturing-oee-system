
def calculate_oee(
    planned_time_seconds: float,
    run_time_seconds: float,
    ideal_cycle_time_seconds: float,
    total_count: int,
    good_count: int,
) -> dict:
    if planned_time_seconds <= 0:
        raise ValueError("Planned time must be greater than zero.")

    if run_time_seconds < 0 or run_time_seconds > planned_time_seconds:
        raise ValueError("Run time must be between zero and planned time.")

    if ideal_cycle_time_seconds <= 0:
        raise ValueError("Ideal cycle time must be greater than zero.")

    if total_count < 0 or good_count < 0 or good_count > total_count:
        raise ValueError("Production counts are invalid.")

    availability = run_time_seconds / planned_time_seconds

    if run_time_seconds == 0:
        performance = 0.0
    else:
        performance = (
            ideal_cycle_time_seconds * total_count / run_time_seconds
        )

    quality = good_count / total_count if total_count > 0 else 0.0

    oee = availability * performance * quality

    return {
        "availability": round(availability, 4),
        "performance": round(performance, 4),
        "quality": round(quality, 4),
        "oee": round(oee, 4),
    }
