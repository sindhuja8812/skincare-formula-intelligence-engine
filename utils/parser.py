
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
    cleaned = name.lower().strip()
    return SYNONYMS.get(cleaned, cleaned)


def parse_ingredients(raw_text: str) -> List[str]:
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
