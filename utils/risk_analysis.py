"""
risk_analysis.py

Formula risk analysis based on ingredient risk_level classifications.
"""

from typing import List

# Valid risk level values in the knowledge base
RISK_LEVELS = {"Low", "Moderate", "High"}


def analyze_risk(matched_ingredients: List[dict]) -> dict:
    """
    Analyse the risk profile of a formula based on ingredient risk levels.

    Counts ingredients by risk level and determines an overall formula risk:
    - High   → 3 or more High-risk ingredients
    - Moderate → 1 or 2 High-risk ingredients
    - Low    → no High-risk ingredients

    Args:
        matched_ingredients: List of ingredient row dicts from the knowledge base.

    Returns:
        dict with keys:
            - "low_risk"      (int): Count of Low risk ingredients.
            - "moderate_risk" (int): Count of Moderate risk ingredients.
            - "high_risk"     (int): Count of High risk ingredients.
            - "overall_risk"  (str): "Low", "Moderate", or "High".

    Raises:
        ValueError: If matched_ingredients is empty.
    """
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

    # Test Case 1 — all low-risk ingredients
    tc1 = get_matched(["ceramide np", "panthenol", "allantoin", "centella asiatica extract"])
    r1 = analyze_risk(tc1)
    assert r1["overall_risk"] == "Low", f"FAIL TC1: {r1}"
    assert r1["high_risk"] == 0, f"FAIL TC1 high count: {r1}"
    print(f"[PASS] TC1 risk (barrier formula): {r1}")

    # Test Case 2 — high-irritant formula (Alcohol Denat, Fragrance, Menthol are all High)
    tc2 = get_matched(["alcohol denat", "fragrance", "menthol"])
    r2 = analyze_risk(tc2)
    assert r2["overall_risk"] == "High", f"FAIL TC2: {r2}"
    assert r2["high_risk"] == 3, f"FAIL TC2 high count: {r2}"
    print(f"[PASS] TC2 risk (irritant formula): {r2}")

    # Test Case 3 — mixed, 1–2 high risk → Moderate overall
    tc3 = get_matched(["niacinamide", "fragrance", "glycerin"])
    r3 = analyze_risk(tc3)
    assert r3["overall_risk"] == "Moderate", f"FAIL TC3: {r3}"
    print(f"[PASS] TC3 risk (mixed formula): {r3}")

    # Edge case — empty list
    try:
        analyze_risk([])
        print("FAIL: should have raised ValueError")
    except ValueError:
        print("[PASS] ValueError raised for empty ingredient list.")
