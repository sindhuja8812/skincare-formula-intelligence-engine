
from typing import List

# Maps skin type labels to their corresponding CSV column names
SKIN_TYPE_COLUMNS: dict[str, str] = {
    "sensitive":   "sensitive_score",
    "oily":        "oily_score",
    "dry":         "dry_score",
    "combination": "combination_score",
    "normal":      "normal_score",
}

ALL_SCORE_COLUMNS: List[str] = list(SKIN_TYPE_COLUMNS.values())

# Realism adjustment — prevents perfect scores given unknown formulation factors
REALISM_FACTOR: float = 0.95
MAX_SCORE: float = 95.0

# Verdict thresholds (applied after realism adjustment)
VERDICT_THRESHOLDS: List[tuple[float, str]] = [
    (85, "Excellent Match"),
    (75, "Very Good Match"),
    (65, "Good Match"),
    (50, "Use With Caution"),
    (0,  "Not Recommended"),
]

SCORE_EXPLANATION: str = (
    "This score reflects ingredient compatibility only. "
    "The analysis does not account for ingredient concentration, "
    "formulation quality, pH, or manufacturing differences."
)


def get_formula_verdict(score: float) -> str:
    for threshold, label in VERDICT_THRESHOLDS:
        if score >= threshold:
            return label
    return "Not Recommended"


def generate_score_explanation() -> str:
    return SCORE_EXPLANATION


def calculate_coverage(
    matched_ingredients: List[dict],
    total_ingredients: int,
) -> dict:
    recognized = len(matched_ingredients)
    coverage = round((recognized / total_ingredients) * 100, 1) if total_ingredients else 0.0
    return {
        "recognized_ingredients": recognized,
        "total_ingredients": total_ingredients,
        "coverage": coverage,
    }


def _apply_realism(raw_score: float) -> float:
    adjusted = raw_score * REALISM_FACTOR
    return round(min(adjusted, MAX_SCORE), 1)


def calculate_skin_match_score(
    matched_ingredients: List[dict],
    skin_type: str,
    total_ingredients: int | None = None,
) -> dict:
    skin_type = skin_type.lower().strip()
    if skin_type not in SKIN_TYPE_COLUMNS:
        raise ValueError(
            f"Unknown skin type '{skin_type}'. "
            f"Valid options: {list(SKIN_TYPE_COLUMNS.keys())}"
        )
    if not matched_ingredients:
        raise ValueError("matched_ingredients must not be empty.")

    column = SKIN_TYPE_COLUMNS[skin_type]
    scores = [ing[column] for ing in matched_ingredients if column in ing]

    if not scores:
        raise ValueError(f"No '{column}' data found in matched ingredients.")

    total = total_ingredients if total_ingredients is not None else len(matched_ingredients)

    raw_score = (sum(scores) / len(scores)) * 10       # 0–10 → 0–100
    score     = _apply_realism(raw_score)               # realism cap

    return {
        "score":       score,
        "verdict":     get_formula_verdict(score),
        "explanation": generate_score_explanation(),
        "coverage":    calculate_coverage(matched_ingredients, total),
    }


def calculate_overall_formula_score(
    matched_ingredients: List[dict],
    total_ingredients: int | None = None,
) -> dict:
    if not matched_ingredients:
        raise ValueError("matched_ingredients must not be empty.")

    all_values: List[float] = []
    for ing in matched_ingredients:
        for col in ALL_SCORE_COLUMNS:
            if col in ing:
                all_values.append(ing[col])

    if not all_values:
        raise ValueError("No score columns found in matched ingredients.")

    total = total_ingredients if total_ingredients is not None else len(matched_ingredients)

    raw_score = (sum(all_values) / len(all_values)) * 10   # 0–10 → 0–100
    score     = _apply_realism(raw_score)                   # realism cap

    return {
        "score":       score,
        "verdict":     get_formula_verdict(score),
        "explanation": generate_score_explanation(),
        "coverage":    calculate_coverage(matched_ingredients, total),
    }


