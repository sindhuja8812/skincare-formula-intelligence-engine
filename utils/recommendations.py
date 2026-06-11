
from typing import List

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils.scorer import SKIN_TYPE_COLUMNS

# ---------------------------------------------------------------------------
# Skin-type preferred ingredient lists (canonical lowercase names)
# ---------------------------------------------------------------------------
PREFERRED_BY_SKIN_TYPE: dict[str, List[str]] = {
    "sensitive": [
        "ceramide np",
        "panthenol",
        "allantoin",
        "centella asiatica extract",
        "beta glucan",
        "aloe vera",
    ],
    "oily": [
        "niacinamide",
        "salicylic acid",
        "zinc pca",
        "green tea extract",
    ],
    "dry": [
        "ceramide np",
        "squalane",
        "glycerin",
        "hyaluronic acid",
        "urea",
        "petrolatum",
    ],
    "combination": [
        "niacinamide",
        "panthenol",
        "glycerin",
        "green tea extract",
    ],
    "normal": [
        "niacinamide",
        "panthenol",
        "ceramide np",
    ],
}

# Ingredients that are problematic for each skin type (canonical lowercase names)
AVOID_BY_SKIN_TYPE: dict[str, List[str]] = {
    "sensitive": [
        "fragrance",
        "menthol",
        "alcohol denat",
        "peppermint oil",
        "eucalyptus oil",
        "sodium lauryl sulfate",
        "clove oil",
        "cinnamon extract",
    ],
    "dry": [
        "alcohol denat",
        "salicylic acid",
        "sodium lauryl sulfate",
        "witch hazel",
        "benzoyl peroxide",
    ],
    "oily": [
        "petrolatum",
        "mineral oil",
        "cocoa butter",
        "shea butter",
        "coconut oil",
    ],
    "combination": [
        "alcohol denat",
        "fragrance",
        "petrolatum",
    ],
    "normal": [],
}

MAX_RECOMMENDATIONS = 5


def generate_addition_recommendations(
    skin_type: str,
    matched_ingredients: List[dict],
) -> List[str]:
    """
    Recommend beneficial ingredients for the given skin type that are absent
    from the current formula.

    Compares the skin-type preferred list against already-matched ingredient
    names and returns up to MAX_RECOMMENDATIONS missing entries.

    Args:
        skin_type:           One of: sensitive, oily, dry, combination, normal.
        matched_ingredients: List of ingredient row dicts from the knowledge base.

    Returns:
        List[str]: Display-cased ingredient names to consider adding.
                   Returns an empty list if all preferred ingredients are present.

    Raises:
        ValueError: If skin_type is not recognised.
    """
    skin_type = skin_type.lower().strip()
    if skin_type not in PREFERRED_BY_SKIN_TYPE:
        raise ValueError(
            f"Unknown skin type '{skin_type}'. "
            f"Valid options: {list(PREFERRED_BY_SKIN_TYPE.keys())}"
        )

    present = {ing["ingredient"].lower() for ing in matched_ingredients}
    preferred = PREFERRED_BY_SKIN_TYPE[skin_type]

    missing = [name for name in preferred if name not in present]
    return [name.title() for name in missing[:MAX_RECOMMENDATIONS]]


def generate_avoid_recommendations(
    skin_type: str,
    matched_ingredients: List[dict],
) -> List[str]:
    """
    Identify ingredients already in the formula that are problematic for the
    given skin type.

    Compares the skin-type avoid list against already-matched ingredient names
    and returns any matches found.

    Args:
        skin_type:           One of: sensitive, oily, dry, combination, normal.
        matched_ingredients: List of ingredient row dicts from the knowledge base.

    Returns:
        List[str]: Display-cased ingredient names that should be avoided.
                   Returns an empty list if no problematic ingredients are present.

    Raises:
        ValueError: If skin_type is not recognised.
    """
    skin_type = skin_type.lower().strip()
    if skin_type not in AVOID_BY_SKIN_TYPE:
        raise ValueError(
            f"Unknown skin type '{skin_type}'. "
            f"Valid options: {list(AVOID_BY_SKIN_TYPE.keys())}"
        )

    present = {ing["ingredient"].lower() for ing in matched_ingredients}
    avoid = AVOID_BY_SKIN_TYPE[skin_type]

    flagged = [name for name in avoid if name in present]
    return [name.title() for name in flagged]


def get_formula_strengths(
    matched_ingredients: List[dict],
    skin_type: str,
) -> List[str]:
    """
    Return the top-performing ingredients for the given skin type, sorted by
    their skin-type-specific score in descending order.

    Args:
        matched_ingredients: List of ingredient row dicts from the knowledge base.
        skin_type:           One of: sensitive, oily, dry, combination, normal.

    Returns:
        List[str]: Display-cased names of the top 5 strongest ingredients.

    Raises:
        ValueError: If skin_type is not recognised or no ingredients supplied.
    """
    skin_type = skin_type.lower().strip()
    if skin_type not in SKIN_TYPE_COLUMNS:
        raise ValueError(f"Unknown skin type '{skin_type}'.")
    if not matched_ingredients:
        raise ValueError("matched_ingredients must not be empty.")

    col = SKIN_TYPE_COLUMNS[skin_type]
    sorted_ings = sorted(
        matched_ingredients,
        key=lambda ing: ing.get(col, 0),
        reverse=True,
    )
    return [ing["ingredient"].title() for ing in sorted_ings[:MAX_RECOMMENDATIONS]]


def get_formula_weaknesses(
    matched_ingredients: List[dict],
    skin_type: str,
) -> List[str]:
    """
    Return ingredients that are either high-risk or have low compatibility with
    the given skin type, sorted by ascending skin-type score.

    An ingredient is considered a weakness if:
        - risk_level is "High" or "Moderate", OR
        - skin-type-specific score is <= 5 (out of 10)

    Args:
        matched_ingredients: List of ingredient row dicts from the knowledge base.
        skin_type:           One of: sensitive, oily, dry, combination, normal.

    Returns:
        List[str]: Display-cased names of up to 5 weak/risky ingredients.

    Raises:
        ValueError: If skin_type is not recognised or no ingredients supplied.
    """
    skin_type = skin_type.lower().strip()
    if skin_type not in SKIN_TYPE_COLUMNS:
        raise ValueError(f"Unknown skin type '{skin_type}'.")
    if not matched_ingredients:
        raise ValueError("matched_ingredients must not be empty.")

    col = SKIN_TYPE_COLUMNS[skin_type]

    weaknesses = [
        ing for ing in matched_ingredients
        if ing.get("risk_level") in {"High", "Moderate"}
        or ing.get(col, 10) <= 5
    ]

    # Sort by skin-type score ascending (worst first)
    weaknesses.sort(key=lambda ing: ing.get(col, 0))
    return [ing["ingredient"].title() for ing in weaknesses[:MAX_RECOMMENDATIONS]]


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

    # ------------------------------------------------------------------
    # Test Case 1 — sensitive barrier formula (4 of 6 preferred present)
    # ------------------------------------------------------------------
    tc1 = get_matched(["ceramide np", "panthenol", "allantoin", "centella asiatica extract"])
    additions_1 = generate_addition_recommendations("sensitive", tc1)
    avoid_1     = generate_avoid_recommendations("sensitive", tc1)
    strengths_1 = get_formula_strengths(tc1, "sensitive")
    weaknesses_1 = get_formula_weaknesses(tc1, "sensitive")

    assert "Beta Glucan" in additions_1,  f"FAIL TC1 additions: {additions_1}"
    assert "Aloe Vera" in additions_1,    f"FAIL TC1 additions: {additions_1}"
    assert avoid_1 == [],                 f"FAIL TC1 avoid: {avoid_1}"
    assert weaknesses_1 == [],            f"FAIL TC1 weaknesses: {weaknesses_1}"
    print(f"[PASS] TC1 additions  : {additions_1}")
    print(f"[PASS] TC1 avoid      : {avoid_1}")
    print(f"[PASS] TC1 strengths  : {strengths_1}")
    print(f"[PASS] TC1 weaknesses : {weaknesses_1}\n")

    # ------------------------------------------------------------------
    # Test Case 2 — high-irritant formula, sensitive skin
    # ------------------------------------------------------------------
    tc2 = get_matched(["alcohol denat", "fragrance", "menthol"])
    additions_2 = generate_addition_recommendations("sensitive", tc2)
    avoid_2     = generate_avoid_recommendations("sensitive", tc2)
    weaknesses_2 = get_formula_weaknesses(tc2, "sensitive")

    assert "Fragrance" in avoid_2,      f"FAIL TC2 avoid: {avoid_2}"
    assert "Menthol" in avoid_2,        f"FAIL TC2 avoid: {avoid_2}"
    assert "Alcohol Denat" in avoid_2,  f"FAIL TC2 avoid: {avoid_2}"
    assert len(weaknesses_2) == 3,      f"FAIL TC2 weaknesses count: {weaknesses_2}"
    print(f"[PASS] TC2 additions  : {additions_2}")
    print(f"[PASS] TC2 avoid      : {avoid_2}")
    print(f"[PASS] TC2 weaknesses : {weaknesses_2}\n")

    # ------------------------------------------------------------------
    # Test Case 3 — oily skin actives (3 of 4 preferred present)
    # ------------------------------------------------------------------
    tc3 = get_matched(["niacinamide", "salicylic acid", "zinc pca"])
    additions_3 = generate_addition_recommendations("oily", tc3)
    avoid_3     = generate_avoid_recommendations("oily", tc3)

    assert "Green Tea Extract" in additions_3, f"FAIL TC3 additions: {additions_3}"
    print(f"[PASS] TC3 additions  : {additions_3}")
    print(f"[PASS] TC3 avoid      : {avoid_3}")

    # Edge case — invalid skin type
    try:
        generate_addition_recommendations("unknown", tc1)
        print("FAIL: should have raised ValueError")
    except ValueError:
        print("\n[PASS] ValueError raised for unknown skin type.")
