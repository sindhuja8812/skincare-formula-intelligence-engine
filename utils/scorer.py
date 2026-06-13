
from typing import List

# Maps skin-type labels (UI-facing) → CSV column names in the knowledge base
SKIN_TYPE_COLUMNS: dict[str, str] = {
    "sensitive":   "sensitive_score",
    "oily":        "oily_score",
    "dry":         "dry_score",
    "combination": "combination_score",
    "normal":      "normal_score",
}

ALL_SCORE_COLUMNS: List[str] = list(SKIN_TYPE_COLUMNS.values())  # all five column names

# Prevents artificially perfect scores caused by unknown formulation variables.
# 0.90 means even an ideal ingredient list tops out at ~90/100, reflecting
# that concentration, pH, and formulation method are not accounted for.
REALISM_FACTOR: float = 0.90
MAX_SCORE:       float = 90.0

# Threshold → verdict label pairs, checked highest-first.
# Calibrated against the 90-point MAX_SCORE ceiling.
VERDICT_THRESHOLDS: List[tuple[float, str]] = [
    (82, "Excellent Match"),
    (72, "Very Good Match"),
    (62, "Good Match"),
    (48, "Use With Caution"),
    (0,  "Not Recommended"),
]

SCORE_EXPLANATION: str = (
    "This score reflects ingredient compatibility only. "
    "The analysis does not account for ingredient concentration, "
    "formulation quality, pH, or manufacturing differences."
)


def get_formula_verdict(score: float) -> str:
    """Return the human-readable verdict label for a given score."""
    for threshold, label in VERDICT_THRESHOLDS:
        if score >= threshold:                        # first matching band wins
            return label
    return "Not Recommended"


def generate_score_explanation() -> str:
    """Return the standard score disclaimer string."""
    return SCORE_EXPLANATION


def calculate_coverage(matched_ingredients: List[dict], total_ingredients: int) -> dict:
    recognized = len(matched_ingredients)
    coverage   = round((recognized / total_ingredients) * 100, 1) if total_ingredients else 0.0
    return {
        "recognized_ingredients": recognized,
        "total_ingredients":      total_ingredients,
        "coverage":               coverage,
    }


def _apply_realism(raw_score: float) -> float:
    """Scale score by realism factor and cap at MAX_SCORE."""
    adjusted = raw_score * REALISM_FACTOR
    return round(min(adjusted, MAX_SCORE), 1)


# Categories that are functional but don't affect skin compatibility
_SCORE_EXCLUDED_CATEGORIES = {"Excipient", "Preservative"}

def calculate_skin_match_score(
    matched_ingredients: List[dict],
    skin_type: str,
    total_ingredients: int | None = None,
) -> dict:
    skin_type = skin_type.lower().strip()
    if skin_type not in SKIN_TYPE_COLUMNS:
        raise ValueError(f"Unknown skin type '{skin_type}'.")
    if not matched_ingredients:
        raise ValueError("matched_ingredients must not be empty.")

    column = SKIN_TYPE_COLUMNS[skin_type]

    # Score only active/functional ingredients, not excipients/preservatives
    scoreable = [
        ing for ing in matched_ingredients
        if ing.get("category", "") not in _SCORE_EXCLUDED_CATEGORIES
    ]

    # Fall back to all ingredients if nothing passes the filter
    score_source = scoreable if scoreable else matched_ingredients

    scores = [ing[column] for ing in score_source if column in ing]

    if not scores:
        raise ValueError(f"No '{column}' data found in matched ingredients.")

    total     = total_ingredients if total_ingredients is not None else len(matched_ingredients)
    raw_score = (sum(scores) / len(scores)) * 10
    score     = _apply_realism(raw_score)

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

    scoreable = [
        ing for ing in matched_ingredients
        if ing.get("category", "") not in _SCORE_EXCLUDED_CATEGORIES
    ]
    score_source = scoreable if scoreable else matched_ingredients

    all_values: List[float] = []
    for ing in score_source:
        for col in ALL_SCORE_COLUMNS:
            if col in ing:
                all_values.append(ing[col])

    if not all_values:
        raise ValueError("No score columns found in matched ingredients.")

    total     = total_ingredients if total_ingredients is not None else len(matched_ingredients)
    raw_score = (sum(all_values) / len(all_values)) * 10
    score     = _apply_realism(raw_score)

    return {
        "score":       score,
        "verdict":     get_formula_verdict(score),
        "explanation": generate_score_explanation(),
        "coverage":    calculate_coverage(matched_ingredients, total),
    }