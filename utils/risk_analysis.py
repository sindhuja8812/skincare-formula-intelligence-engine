
from typing import List

# Valid risk level values in the knowledge base
RISK_LEVELS = {"Low", "Moderate", "High"}


def analyze_risk(matched_ingredients: List[dict]) -> dict:
    if not matched_ingredients:
        raise ValueError("matched_ingredients must not be empty.")

    counts: dict[str, int] = {"Low": 0, "Moderate": 0, "High": 0}

    for ing in matched_ingredients:
        level = ing.get("risk_level", "Low")
        if level in counts:
            counts[level] += 1

    high = counts["High"]
    if high >= 3:
        overall = "High"
    elif high >= 1:
        overall = "Moderate"
    else:
        overall = "Low"

    return {
        "low_risk": counts["Low"],
        "moderate_risk": counts["Moderate"],
        "high_risk": counts["High"],
        "overall_risk": overall,
    }


