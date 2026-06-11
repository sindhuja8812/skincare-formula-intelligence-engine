"""
parser.py

Handles ingredient text parsing and name normalization.
"""

import re
from typing import List

# ---------------------------------------------------------------------------
# Synonym mapping — maps common aliases to canonical knowledge base names
# ---------------------------------------------------------------------------
SYNONYMS: dict[str, str] = {
    "aqua": "water",
    "sodium hyaluronate": "hyaluronic acid",
    "beta-glucan": "beta glucan",
    "aloe barbadensis leaf juice": "aloe vera",
    "tocopheryl acetate": "vitamin e",
    "centella asiatica": "centella asiatica extract",
}


def normalize_ingredient_name(name: str) -> str:
    """
    Normalize an ingredient name for consistent lookup.

    Steps:
    1. Lowercase and strip whitespace
    2. Apply synonym mapping

    Args:
        name: Raw ingredient name string.

    Returns:
        str: Normalized ingredient name.
    """
    cleaned = name.lower().strip()
    return SYNONYMS.get(cleaned, cleaned)


def parse_ingredients(raw_text: str) -> List[str]:
    """
    Parse a raw ingredient list string into a clean, normalized list.

    Supports separators: newline, comma, semicolon (and mixed combinations).
    Deduplicates while preserving first-occurrence order.

    Args:
        raw_text: Raw ingredient string from user input or product label.

    Returns:
        List[str]: Ordered, deduplicated list of normalized ingredient names.

    Example:
        >>> parse_ingredients("Water, Glycerin, Niacinamide")
        ['water', 'glycerin', 'niacinamide']
    """
    # Split on comma, semicolon, or newline
    tokens = re.split(r"[,;\n]+", raw_text)

    seen: set[str] = set()
    result: List[str] = []

    for token in tokens:
        normalized = normalize_ingredient_name(token)
        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(normalized)

    return result


# ---------------------------------------------------------------------------
# Test section
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Test Case 1 — newline-separated, with centella asiatica synonym
    input_1 = "Ceramide NP\nPanthenol\nCentella Asiatica"
    expected_1 = ["ceramide np", "panthenol", "centella asiatica extract"]
    result_1 = parse_ingredients(input_1)
    assert result_1 == expected_1, f"FAIL: {result_1}"
    print(f"[PASS] Test Case 1: {result_1}")

    # Test Case 2 — newline-separated, with synonym mapping
    input_2 = "Aqua\nSodium Hyaluronate\nBeta-Glucan"
    expected_2 = ["water", "hyaluronic acid", "beta glucan"]
    result_2 = parse_ingredients(input_2)
    assert result_2 == expected_2, f"FAIL: {result_2}"
    print(f"[PASS] Test Case 2: {result_2}")

    # Comma-separated
    result_3 = parse_ingredients("Water, Glycerin, Niacinamide")
    assert result_3 == ["water", "glycerin", "niacinamide"], f"FAIL: {result_3}"
    print(f"[PASS] Comma-separated: {result_3}")

    # Semicolon-separated
    result_4 = parse_ingredients("Water; Glycerin; Niacinamide")
    assert result_4 == ["water", "glycerin", "niacinamide"], f"FAIL: {result_4}"
    print(f"[PASS] Semicolon-separated: {result_4}")

    # Mixed separators
    result_5 = parse_ingredients("Water, Glycerin;\nNiacinamide")
    assert result_5 == ["water", "glycerin", "niacinamide"], f"FAIL: {result_5}"
    print(f"[PASS] Mixed separators: {result_5}")

    # Deduplication
    result_6 = parse_ingredients("Glycerin, Glycerin, Water")
    assert result_6 == ["glycerin", "water"], f"FAIL: {result_6}"
    print(f"[PASS] Deduplication: {result_6}")
