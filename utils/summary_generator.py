"""
summary_generator.py

Human-readable formula summary and final recommendation generation.

Summaries are constructed from structured data — no AI, no generic text.
Each summary reflects the actual score, risk level, ingredients, and concerns
detected in the formula.
"""

from typing import List

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils.scorer import get_formula_verdict

# ---------------------------------------------------------------------------
# Score band definitions used for summary tone selection
# ---------------------------------------------------------------------------
_EXCELLENT  = 85
_VERY_GOOD  = 75
_GOOD       = 65
_CAUTION    = 50


def _score_band(score: float) -> str:
    """Return an internal band label for the given score."""
    if score >= _EXCELLENT:
        return "excellent"
    if score >= _VERY_GOOD:
        return "very_good"
    if score >= _GOOD:
        return "good"
    if score >= _CAUTION:
        return "caution"
    return "poor"


def generate_formula_summary(
    skin_type: str,
    compatibility_score: float,
    risk_level: str,
    benefits: List[str],
    concerns: List[str],
    strengths: List[str],
    weaknesses: List[str],
) -> str:
    """
    Generate a concise, professional, human-readable formula summary.

    The summary tone scales with the compatibility score and is grounded in
    the actual detected benefits, concerns, strengths, and weaknesses —
    not generic filler text.

    Args:
        skin_type:            Skin type label (e.g. "sensitive").
        compatibility_score:  Realism-adjusted 0–95 skin match score.
        risk_level:           Overall risk: "Low", "Moderate", or "High".
        benefits:             Top detected formula benefits.
        concerns:             Detected formula concerns.
        strengths:            Top-performing ingredient names.
        weaknesses:           High-risk or low-compatibility ingredient names.

    Returns:
        str: A single-paragraph professional summary.
    """
    skin_label  = skin_type.lower().strip()
    band        = _score_band(compatibility_score)
    top_strengths = strengths[:3]
    top_concerns  = weaknesses[:3]

    # Opening sentence — score-dependent
    if band == "excellent":
        opening = (
            f"This formulation appears highly compatible with {skin_label} skin. "
            f"The ingredient profile is well-suited to this skin type, "
            f"with a compatibility score of {compatibility_score}/100."
        )
    elif band == "very_good":
        opening = (
            f"This formulation is a strong match for {skin_label} skin, "
            f"achieving a compatibility score of {compatibility_score}/100. "
            f"Most ingredients are well-tolerated for this skin type."
        )
    elif band == "good":
        opening = (
            f"This formulation shows reasonable compatibility with {skin_label} skin "
            f"(score: {compatibility_score}/100). "
            f"The formula performs adequately but has room for improvement."
        )
    elif band == "caution":
        opening = (
            f"This formulation has limited compatibility with {skin_label} skin "
            f"(score: {compatibility_score}/100). "
            f"Several ingredients may not suit this skin type and warrant review."
        )
    else:
        opening = (
            f"This formulation is not well-suited for {skin_label} skin "
            f"(score: {compatibility_score}/100). "
            f"A significant number of ingredients are poorly tolerated by this skin type."
        )

    # Benefits sentence
    if benefits:
        benefit_list = ", ".join(benefits[:4])
        benefit_sentence = f"Key formula benefits include {benefit_list}."
    else:
        benefit_sentence = "No notable formula benefits were detected."

    # Strengths sentence
    if top_strengths:
        strength_list = ", ".join(top_strengths)
        strength_sentence = (
            f"Standout ingredients contributing to compatibility include "
            f"{strength_list}."
        )
    else:
        strength_sentence = ""

    # Risk / concerns sentence
    if risk_level == "Low" and not concerns:
        risk_sentence = "No major irritants were detected and the overall risk profile is low."
    elif risk_level == "Low" and concerns:
        concern_list = ", ".join(concerns[:3])
        risk_sentence = (
            f"The overall risk level is low, though minor concerns "
            f"({concern_list}) were noted."
        )
    elif risk_level == "Moderate":
        if top_concerns:
            concern_list = ", ".join(top_concerns)
            risk_sentence = (
                f"The formula carries a moderate risk profile. "
                f"Ingredients of concern include {concern_list}. "
                f"Patch testing is advisable."
            )
        else:
            risk_sentence = (
                "The formula carries a moderate risk profile. Patch testing is advisable."
            )
    else:  # High
        if top_concerns:
            concern_list = ", ".join(top_concerns)
            risk_sentence = (
                f"Multiple ingredients associated with irritation risk were identified, "
                f"including {concern_list}. "
                f"Users with {skin_label} skin may experience redness, dryness, or irritation."
            )
        else:
            risk_sentence = (
                f"The formula carries a high risk profile. "
                f"Users with {skin_label} skin may experience adverse reactions."
            )

    parts = [opening, benefit_sentence]
    if strength_sentence:
        parts.append(strength_sentence)
    parts.append(risk_sentence)

    return " ".join(parts)


def get_final_recommendation(score: float) -> str:
    """
    Return a final recommendation label based on the compatibility score.

    Thresholds:
        >= 85  → Excellent Match
        75–84  → Very Good Match
        65–74  → Good Match
        50–64  → Use With Caution
        < 50   → Not Recommended

    Args:
        score: Realism-adjusted compatibility score (0–95).

    Returns:
        str: Final recommendation label.
    """
    return get_formula_verdict(score)


# ---------------------------------------------------------------------------
# Test section
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

    from utils.knowledge_loader import load_knowledge_base, find_ingredient
    from utils.scorer import calculate_skin_match_score, calculate_overall_formula_score
    from utils.risk_analysis import analyze_risk
    from utils.benefits import extract_benefits, extract_concerns
    from utils.recommendations import (
        generate_addition_recommendations,
        generate_avoid_recommendations,
        get_formula_strengths,
        get_formula_weaknesses,
    )

    kb = load_knowledge_base()

    def get_matched(names: List[str]) -> List[dict]:
        results = [find_ingredient(n, kb) for n in names]
        return [r for r in results if r is not None]

    def run_full_analysis(names: List[str], skin_type: str, label: str) -> None:
        matched  = get_matched(names)
        total    = len(names)

        skin     = calculate_skin_match_score(matched, skin_type, total_ingredients=total)
        risk     = analyze_risk(matched)
        benefits = extract_benefits(matched)
        concerns = extract_concerns(matched)
        strengths   = get_formula_strengths(matched, skin_type)
        weaknesses  = get_formula_weaknesses(matched, skin_type)
        additions   = generate_addition_recommendations(skin_type, matched)
        avoid       = generate_avoid_recommendations(skin_type, matched)
        rec         = get_final_recommendation(skin["score"])
        summary     = generate_formula_summary(
            skin_type          = skin_type,
            compatibility_score = skin["score"],
            risk_level         = risk["overall_risk"],
            benefits           = benefits,
            concerns           = concerns,
            strengths          = strengths,
            weaknesses         = weaknesses,
        )

        print(f"\n{'=' * 60}")
        print(f"  {label}")
        print(f"{'=' * 60}")
        print(f"  Compatibility Score : {skin['score']}/100")
        print(f"  Recommendation      : {rec}")
        print(f"  Risk Level          : {risk['overall_risk']}")
        print(f"  Strengths           : {strengths}")
        print(f"  Weaknesses          : {weaknesses}")
        print(f"  Add to Formula      : {additions}")
        print(f"  Avoid               : {avoid}")
        print(f"\n  Summary:\n  {summary}")
        print(f"{'=' * 60}")

        return skin["score"], rec, risk["overall_risk"], additions, avoid

    # ------------------------------------------------------------------
    # Test Case 1 — sensitive barrier formula
    # ------------------------------------------------------------------
    score, rec, risk_level, additions, avoid = run_full_analysis(
        ["ceramide np", "panthenol", "allantoin", "centella asiatica extract"],
        "sensitive",
        "TC1 — Sensitive Barrier Formula",
    )
    assert score >= 85,                      f"FAIL TC1 score: {score}"
    assert rec == "Excellent Match",         f"FAIL TC1 rec: {rec}"
    assert risk_level == "Low",              f"FAIL TC1 risk: {risk_level}"
    assert "Beta Glucan" in additions,       f"FAIL TC1 additions: {additions}"
    assert "Aloe Vera" in additions,         f"FAIL TC1 additions: {additions}"
    assert avoid == [],                      f"FAIL TC1 avoid: {avoid}"
    print("[PASS] TC1 all assertions passed.")

    # ------------------------------------------------------------------
    # Test Case 2 — high-irritant formula, sensitive skin
    # ------------------------------------------------------------------
    score2, rec2, risk2, additions2, avoid2 = run_full_analysis(
        ["alcohol denat", "fragrance", "menthol"],
        "sensitive",
        "TC2 — Sensitive High-Irritant Formula",
    )
    assert score2 < 50,                      f"FAIL TC2 score: {score2}"
    assert rec2 == "Not Recommended",        f"FAIL TC2 rec: {rec2}"
    assert risk2 == "High",                  f"FAIL TC2 risk: {risk2}"
    assert "Fragrance" in avoid2,            f"FAIL TC2 avoid: {avoid2}"
    assert "Menthol" in avoid2,              f"FAIL TC2 avoid: {avoid2}"
    assert "Alcohol Denat" in avoid2,        f"FAIL TC2 avoid: {avoid2}"
    print("[PASS] TC2 all assertions passed.")

    # ------------------------------------------------------------------
    # Test Case 3 — oily skin actives
    # ------------------------------------------------------------------
    score3, rec3, risk3, additions3, avoid3 = run_full_analysis(
        ["niacinamide", "salicylic acid", "zinc pca"],
        "oily",
        "TC3 — Oily Skin Actives Formula",
    )
    assert score3 >= 75,                         f"FAIL TC3 score: {score3}"
    assert rec3 in ("Very Good Match", "Excellent Match"), f"FAIL TC3 rec: {rec3}"
    assert "Green Tea Extract" in additions3,     f"FAIL TC3 additions: {additions3}"
    print("[PASS] TC3 all assertions passed.")
