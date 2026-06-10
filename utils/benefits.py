"""
benefits.py

Benefit and concern extraction from a matched ingredient list.
"""

from collections import Counter
from typing import List


def _split_pipe_column(matched_ingredients: List[dict], column: str) -> List[str]:
    """
    Internal helper: collect and split all pipe-separated values from a column.

    Args:
        matched_ingredients: List of ingredient row dicts.
        column:              Column name to read ("benefits" or "concerns").

    Returns:
        Flat list of individual values (with "None" entries excluded).
    """
    values: List[str] = []
    for ing in matched_ingredients:
        raw = ing.get(column, "None") or "None"
        for item in raw.split("|"):
            item = item.strip()
            if item and item.lower() != "none":
                values.append(item)
    return values


def extract_benefits(matched_ingredients: List[dict]) -> List[str]:
    """
    Extract and rank formula benefits by frequency across all matched ingredients.

    Reads the pipe-separated benefits column, counts each benefit occurrence,
    and returns them sorted from most to least frequent.

    Args:
        matched_ingredients: List of ingredient row dicts from the knowledge base.

    Returns:
        List[str]: Benefits sorted by descending frequency.
                   Returns an empty list if no benefits are found.
    """
    values = _split_pipe_column(matched_ingredients, "benefits")
    counts = Counter(values)
    return [benefit for benefit, _ in counts.most_common()]


def extract_concerns(matched_ingredients: List[dict]) -> List[str]:
    """
    Extract and rank formula concerns by frequency across all matched ingredients.

    Reads the pipe-separated concerns column, counts each concern occurrence,
    and returns them sorted from most to least frequent.

    Args:
        matched_ingredients: List of ingredient row dicts from the knowledge base.

    Returns:
        List[str]: Concerns sorted by descending frequency.
                   Returns an empty list if no concerns are found.
    """
    values = _split_pipe_column(matched_ingredients, "concerns")
    counts = Counter(values)
    return [concern for concern, _ in counts.most_common()]


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

    # Test Case 1 — barrier / soothing formula
    tc1 = get_matched(["ceramide np", "panthenol", "allantoin", "centella asiatica extract"])
    benefits_1 = extract_benefits(tc1)
    assert "Barrier Repair" in benefits_1, f"FAIL TC1 benefits: {benefits_1}"
    assert "Soothing" in benefits_1, f"FAIL TC1 benefits: {benefits_1}"
    assert "Hydration" in benefits_1, f"FAIL TC1 benefits: {benefits_1}"
    print(f"[PASS] TC1 benefits: {benefits_1}")

    concerns_1 = extract_concerns(tc1)
    print(f"[PASS] TC1 concerns: {concerns_1}")

    # Test Case 2 — high-irritant formula
    tc2 = get_matched(["alcohol denat", "fragrance", "menthol"])
    concerns_2 = extract_concerns(tc2)
    assert "Irritation Risk" in concerns_2, f"FAIL TC2 concerns: {concerns_2}"
    assert "Sensitivity Trigger" in concerns_2, f"FAIL TC2 concerns: {concerns_2}"
    print(f"[PASS] TC2 concerns: {concerns_2}")

    # Test Case 3 — oily skin actives
    tc3 = get_matched(["niacinamide", "salicylic acid", "zinc pca"])
    benefits_3 = extract_benefits(tc3)
    assert "Oil Control" in benefits_3, f"FAIL TC3 benefits: {benefits_3}"
    assert "Acne Support" in benefits_3, f"FAIL TC3 benefits: {benefits_3}"
    assert "Pore Care" in benefits_3, f"FAIL TC3 benefits: {benefits_3}"
    print(f"[PASS] TC3 benefits: {benefits_3}")

    # Edge case — formula with no concerns
    tc4 = get_matched(["glycerin", "hyaluronic acid"])
    concerns_4 = extract_concerns(tc4)
    assert concerns_4 == [], f"FAIL TC4 empty concerns: {concerns_4}"
    print(f"[PASS] TC4 empty concerns: {concerns_4}")
