"""XP rules and level calculation for the Study RPG dashboard."""

XP_RULES = {
    "applied_morning_100": 1000,
    "applied_afternoon_1": 300,
    "hazardous_practice_set": 800,
    "chemical_added": 200,
    "chemical_level_up": 100,
}

LEVEL_THRESHOLDS = [
    (10, 30000),
    (9, 23000),
    (8, 17000),
    (7, 12000),
    (6, 8000),
    (5, 5000),
    (4, 3000),
    (3, 1500),
    (2, 500),
    (1, 0),
]


def calculate_level(total_xp: int) -> int:
    """Return the current level for the given total XP."""
    for level, threshold in LEVEL_THRESHOLDS:
        if total_xp >= threshold:
            return level
    return 1


def next_level_xp(total_xp: int) -> int | None:
    """Return the XP required for the next level, or None at max level."""
    current_level = calculate_level(total_xp)
    if current_level >= 10:
        return None

    for level, threshold in sorted(LEVEL_THRESHOLDS):
        if level == current_level + 1:
            return threshold
    return None


def progress_to_next_level(total_xp: int) -> float:
    """Return progress to the next level as a value between 0.0 and 1.0."""
    current_level = calculate_level(total_xp)
    next_threshold = next_level_xp(total_xp)
    if next_threshold is None:
        return 1.0

    current_threshold = 0
    for level, threshold in LEVEL_THRESHOLDS:
        if level == current_level:
            current_threshold = threshold
            break

    span = next_threshold - current_threshold
    if span <= 0:
        return 1.0
    return max(0.0, min(1.0, (total_xp - current_threshold) / span))
