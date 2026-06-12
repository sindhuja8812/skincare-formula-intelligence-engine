from collections import Counter
from typing import List

# Minimum number of ingredients that must share a concern before it is surfaced.
# Setting this to 2 prevents single-ingredient edge-case flags from cluttering
# the UI on otherwise low-risk formulas.
_CONCERN_MIN_COUNT = 2


def _split_pipe_column(matched_ingredients: List[dict], column: str) -> List[str]:
    values: List[str] = []
    for ing in matched_ingredients:
        raw = ing.get(column, "None") or "None"
        for item in raw.split("|"):
            item = item.strip()
            if item and item.lower() != "none":
                values.append(item)
    return values


def extract_benefits(matched_ingredients: List[dict]) -> List[str]:
    """Return all benefits sorted by frequency (most common first)."""
    values = _split_pipe_column(matched_ingredients, "benefits")
    counts = Counter(values)
    return [benefit for benefit, _ in counts.most_common()]


def extract_concerns(matched_ingredients: List[dict]) -> List[str]:
    values = _split_pipe_column(matched_ingredients, "concerns")
    counts = Counter(values)

    n = len(matched_ingredients)
    threshold = _CONCERN_MIN_COUNT if n >= 3 else 1

    return [
        concern
        for concern, count in counts.most_common()
        if count >= threshold
    ]