from collections import Counter
from typing import List


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
    values = _split_pipe_column(matched_ingredients, "benefits")
    counts = Counter(values)
    return [benefit for benefit, _ in counts.most_common()]


def extract_concerns(matched_ingredients: List[dict]) -> List[str]:
    values = _split_pipe_column(matched_ingredients, "concerns")
    counts = Counter(values)
    return [concern for concern, _ in counts.most_common()]

