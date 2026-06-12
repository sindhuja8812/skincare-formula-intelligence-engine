from typing import List
import pandas as pd
from .knowledge_loader import load_knowledge_base

RISK_LEVELS = {"Low", "Moderate", "High"}

# Maps skin type label -> the CSV column that holds its risk value
_SKIN_RISK_COLUMNS: dict[str, str] = {
    "sensitive":   "sensitive_risk",
    "oily":        "oily_risk",
    "dry":         "dry_risk",
    "combination": "combination_risk",
    "normal":      "normal_risk",
}


def analyze_risk(matched_ingredients: List[dict], skin_type: str = "normal") -> dict:
    if not matched_ingredients:
        raise ValueError("matched_ingredients must not be empty.")

    skin_type = skin_type.lower().strip()
    risk_col  = _SKIN_RISK_COLUMNS.get(skin_type, "normal_risk")

    counts: dict[str, int] = {"Low": 0, "Moderate": 0, "High": 0}

    for ing in matched_ingredients:
        # Prefer skin-type-specific column; fall back to global risk_level
        level = ing.get(risk_col) or ing.get("risk_level", "Low")
        if level in counts:
            counts[level] += 1

    high     = counts["High"]
    moderate = counts["Moderate"]

    if high >= 3:
        overall = "High"
    elif high >= 1 or moderate >= 3:
        overall = "High"
    elif moderate >= 1:
        overall = "Moderate"
    else:
        overall = "Low"

    return {
        "low_risk":      counts["Low"],
        "moderate_risk": counts["Moderate"],
        "high_risk":     counts["High"],
        "overall_risk":  overall,
    }


def fetch_risks_from_csv() -> dict:
    """Fetch all risks from the ingredient knowledge base CSV."""
    df = load_knowledge_base()
    risks = {}
    
    for _, row in df.iterrows():
        ingredient = row["ingredient"]
        risks[ingredient] = {
            "risk_level": row["risk_level"],
            "sensitive_risk": row.get("sensitive_risk", "Low"),
            "oily_risk": row.get("oily_risk", "Low"),
            "dry_risk": row.get("dry_risk", "Low"),
            "combination_risk": row.get("combination_risk", "Low"),
            "normal_risk": row.get("normal_risk", "Low"),
            "concerns": row.get("concerns", "None"),
        }
    
    return risks