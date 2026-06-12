

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

    # Opening bullet — score-dependent
    if band == "excellent":
        opening = f"Excellent match for {skin_label} skin (score: {compatibility_score}/100)"
    elif band == "very_good":
        opening = f"Strong match for {skin_label} skin (score: {compatibility_score}/100)"
    elif band == "good":
        opening = f"Good compatibility with {skin_label} skin (score: {compatibility_score}/100)"
    elif band == "caution":
        opening = f"Limited compatibility with {skin_label} skin (score: {compatibility_score}/100)"
    else:
        opening = f"Poor compatibility with {skin_label} skin (score: {compatibility_score}/100)"

    # Risk profile bullet
    if risk_level == "Low":
        risk_bullet = "Low irritation risk"
    elif risk_level == "Moderate":
        risk_bullet = "Moderate irritation risk — patch testing recommended"
    else:
        risk_bullet = "High irritation risk — caution advised"

    # Benefits bullet
    if benefits:
        benefit_list = ", ".join(benefits[:3])
        benefits_bullet = f"Key benefits: {benefit_list}"
    else:
        benefits_bullet = "No notable benefits detected"

    # Strengths bullet
    if top_strengths:
        strength_list = ", ".join(top_strengths)
        strengths_bullet = f"Standout ingredients: {strength_list}"
    else:
        strengths_bullet = None

    # Build bullet list
    bullets = [
        f"• {opening}",
        f"• {risk_bullet}",
        f"• {benefits_bullet}",
    ]
    
    if strengths_bullet:
        bullets.append(f"• {strengths_bullet}")
    
    if not concerns:
        bullets.append("• No major concerns detected")

    return "\n".join(bullets)


def get_final_recommendation(score: float) -> str:
    return get_formula_verdict(score)