"""
scorer.py

Skin-type match scoring and overall formula quality scoring.

Scoring philosophy:
    Scores reflect ingredient-level compatibility only. The system has no
    knowledge of concentration, pH, formulation method, stability, or
    manufacturing quality. A realism factor (0.95) and hard cap (95) are
    applied to every score to prevent misleading perfect results.
"""

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
    """
    Map a 0–100 score to a human-readable verdict.

    Thresholds:
        85–95  → Excellent Match
        75–84  → Very Good Match
        65–74  → Good Match
        50–64  → Use With Caution
        <50    → Not Recommended

    Args:
        score: Realism-adjusted score between 0 and 95.

    Returns:
        str: Verdict label.
    """
    for threshold, label in VERDICT_THRESHOLDS:
        if score >= threshold:
            return label
    return "Not Recommended"


def generate_score_explanation() -> str:
    """
    Return a fixed transparency disclaimer for all formula scores.

    Returns:
        str: Explanation of what the score does and does not represent.
    """
    return SCORE_EXPLANATION


def calculate_coverage(
    matched_ingredients: List[dict],
    total_ingredients: int,
) -> dict:
    """
    Calculate what proportion of the submitted formula was recognised.

    Args:
        matched_ingredients: Ingredient dicts successfully found in the KB.
        total_ingredients:   Total number of ingredients submitted by the user.

    Returns:
        dict with keys:
            - "recognized_ingredients" (int)
            - "total_ingredients"      (int)
            - "coverage"               (float): 0–100 percentage.
    """
    recognized = len(matched_ingredients)
    coverage = round((recognized / total_ingredients) * 100, 1) if total_ingredients else 0.0
    return {
        "recognized_ingredients": recognized,
        "total_ingredients": total_ingredients,
        "coverage": coverage,
    }


def _apply_realism(raw_score: float) -> float:
    """
    Apply realism factor and hard cap to a raw 0–100 score.

    Steps:
        1. Multiply by REALISM_FACTOR (0.95) to discount unknown variables.
        2. Clamp to MAX_SCORE (95) so perfect scores are never returned.

    Args:
        raw_score: Score on 0–100 scale before realism adjustment.

    Returns:
        float: Adjusted score, rounded to 1 decimal place.
    """
    adjusted = raw_score * REALISM_FACTOR
    return round(min(adjusted, MAX_SCORE), 1)


def calculate_skin_match_score(
    matched_ingredients: List[dict],
    skin_type: str,
    total_ingredients: int | None = None,
) -> dict:
    """
    Calculate how well a formula matches a given skin type.

    Averages the skin-type-specific score column across all matched
    ingredients, converts from 0–10 to 0–100, then applies a realism
    adjustment before returning a structured result.

    Args:
        matched_ingredients: List of ingredient row dicts from the knowledge base.
        skin_type:           One of: sensitive, oily, dry, combination, normal.
        total_ingredients:   Optional total count submitted (for coverage metric).
                             Defaults to len(matched_ingredients) if not provided.

    Returns:
        dict with keys:
            - "score"       (float): Realism-adjusted 0–95 compatibility score.
            - "verdict"     (str):   Human-readable verdict label.
            - "explanation" (str):   Transparency disclaimer.
            - "coverage"    (dict):  recognized / total / coverage %.

    Raises:
        ValueError: If skin_type is not recognised or no ingredients supplied.
    """
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
    """
    Calculate an overall formula quality score independent of skin type.

    Averages all five skin-type score columns across all matched ingredients,
    converts from 0–10 to 0–100, then applies a realism adjustment.

    Args:
        matched_ingredients: List of ingredient row dicts from the knowledge base.
        total_ingredients:   Optional total count submitted (for coverage metric).
                             Defaults to len(matched_ingredients) if not provided.

    Returns:
        dict with keys:
            - "score"       (float): Realism-adjusted 0–95 quality score.
            - "verdict"     (str):   Human-readable verdict label.
            - "explanation" (str):   Transparency disclaimer.
            - "coverage"    (dict):  recognized / total / coverage %.

    Raises:
        ValueError: If no ingredients are supplied.
    """
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


# ---------------------------------------------------------------------------
# Test section
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

    from utils.knowledge_loader import load_knowledge_base, find_ingredient

    kb = load_knowledge_base()

    def get_matched(names: List[str]) -> List[dict]:
        results = [find_ingredient(n, kb) for n in names]
        return [r for r in results if r is not None]

    # -----------------------------------------------------------------------
    # Test Case 1 — barrier/soothing formula, sensitive skin
    # -----------------------------------------------------------------------
    tc1 = get_matched(["ceramide np", "panthenol", "allantoin", "centella asiatica extract"])
    r1  = calculate_skin_match_score(tc1, "sensitive", total_ingredients=4)

    assert r1["score"] < 100,               f"FAIL: score must never be 100 — got {r1['score']}"
    assert r1["score"] <= MAX_SCORE,        f"FAIL: score exceeds cap — got {r1['score']}"
    assert r1["score"] >= 85,               f"FAIL TC1 skin match too low: {r1['score']}"
    assert r1["verdict"] == "Excellent Match", f"FAIL TC1 verdict: {r1['verdict']}"
    assert "concentration" in r1["explanation"]
    assert r1["coverage"]["recognized_ingredients"] == 4
    assert r1["coverage"]["coverage"] == 100.0
    print(f"[PASS] TC1 skin match (sensitive): score={r1['score']}  verdict='{r1['verdict']}'")
    print(f"       coverage={r1['coverage']}")
    print(f"       explanation: {r1['explanation']}\n")

    q1 = calculate_overall_formula_score(tc1, total_ingredients=4)
    assert q1["score"] <= MAX_SCORE,        f"FAIL TC1 quality cap: {q1['score']}"
    assert q1["score"] >= 80,               f"FAIL TC1 quality too low: {q1['score']}"
    print(f"[PASS] TC1 formula quality: score={q1['score']}  verdict='{q1['verdict']}'\n")

    # -----------------------------------------------------------------------
    # Test Case 2 — high-irritant formula, sensitive skin
    # -----------------------------------------------------------------------
    tc2 = get_matched(["alcohol denat", "fragrance", "menthol"])
    r2  = calculate_skin_match_score(tc2, "sensitive", total_ingredients=3)

    assert r2["score"] < 40,               f"FAIL TC2 skin match too high: {r2['score']}"
    assert r2["verdict"] == "Not Recommended", f"FAIL TC2 verdict: {r2['verdict']}"
    print(f"[PASS] TC2 skin match (sensitive): score={r2['score']}  verdict='{r2['verdict']}'\n")

    # -----------------------------------------------------------------------
    # Test Case 3 — oily skin actives
    # -----------------------------------------------------------------------
    tc3 = get_matched(["niacinamide", "salicylic acid", "zinc pca"])
    r3  = calculate_skin_match_score(tc3, "oily", total_ingredients=3)

    assert r3["score"] >= 80,              f"FAIL TC3 skin match too low: {r3['score']}"
    assert r3["score"] <= MAX_SCORE,       f"FAIL TC3 score exceeds cap: {r3['score']}"
    print(f"[PASS] TC3 skin match (oily): score={r3['score']}  verdict='{r3['verdict']}'\n")

    # -----------------------------------------------------------------------
    # Coverage — partial match (some unknown ingredients)
    # -----------------------------------------------------------------------
    tc4 = get_matched(["glycerin", "hyaluronic acid"])
    r4  = calculate_skin_match_score(tc4, "dry", total_ingredients=5)  # 2 of 5 recognised

    assert r4["coverage"]["recognized_ingredients"] == 2
    assert r4["coverage"]["total_ingredients"] == 5
    assert r4["coverage"]["coverage"] == 40.0
    print(f"[PASS] Partial coverage: {r4['coverage']}\n")

    # -----------------------------------------------------------------------
    # Edge case — invalid skin type
    # -----------------------------------------------------------------------
    try:
        calculate_skin_match_score(tc1, "unknown")
        print("FAIL: should have raised ValueError")
    except ValueError:
        print("[PASS] ValueError raised for unknown skin type.")
