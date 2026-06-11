

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
    return get_formula_verdict(score)