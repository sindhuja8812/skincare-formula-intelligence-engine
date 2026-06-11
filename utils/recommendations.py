
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
