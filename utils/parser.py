
import re
from typing import List

# ---------------------------------------------------------------------------
# Synonym mapping — maps common aliases to canonical knowledge base names
# ---------------------------------------------------------------------------
SYNONYMS: dict[str, str] ={
    # Water
    "aqua": "water",

    # Hyaluronic Acid
    "sodium hyaluronate": "hyaluronic acid",
    "hydrolyzed hyaluronic acid": "hyaluronic acid",

    # Aloe
    "aloe barbadensis leaf juice": "aloe vera",
    "aloe barbadensis": "aloe vera",

    # Vitamin E
    "tocopheryl acetate": "vitamin e",
    "tocopherol": "vitamin e",

    # Vitamin C
    "ascorbic acid": "vitamin c",
    "sodium ascorbyl phosphate": "vitamin c",
    "magnesium ascorbyl phosphate": "vitamin c",
    "ethyl ascorbic acid": "vitamin c",
    "3-o-ethyl ascorbic acid": "vitamin c",

    # Ceramides
    "ceramide np": "ceramide",
    "ceramide ap": "ceramide",
    "ceramide eop": "ceramide",
    "ceramide ns": "ceramide",
    "ceramide": "ceramide",

    # Centella
    "centella asiatica": "centella asiatica extract",
    "cica": "centella asiatica extract",
    "gotu kola": "centella asiatica extract",

    # Green Tea
    "camellia sinensis leaf extract": "green tea extract",
    "green tea": "green tea extract",

    # Tea Tree
    "melaleuca alternifolia leaf oil": "tea tree oil",
    "tea tree": "tea tree oil",

    # Beta Glucan
    "beta-glucan": "beta glucan",
    "β-glucan": "beta glucan",

    # Niacinamide
    "nicotinamide": "niacinamide",

    # Salicylic Acid
    "bha": "salicylic acid",

    # Retinol Family
    "retinyl palmitate": "retinol",
    "retinal": "retinol",
    "retinaldehyde": "retinol",

    # Panthenol
    "d-panthenol": "panthenol",
    "provitamin b5": "panthenol",

    # Alpha Arbutin
    "arbutin": "alpha arbutin",

    # Licorice
    "glycyrrhiza glabra root extract": "licorice root extract",

    # Zinc PCA
    "zinc pca": "zinc pca",

    # Shea Butter
    "butyrospermum parkii butter": "shea butter",

    # Squalane
    "olive squalane": "squalane",
    "sugarcane squalane": "squalane",

    # Fragrance
    "parfum": "fragrance",
    "perfume": "fragrance",

    # Alcohol
    "alcohol denat.": "alcohol denat",
    "denatured alcohol": "alcohol denat",

    # Peptides
    "peptide": "peptides",
    "acetyl hexapeptide-8": "peptides",
    "palmitoyl tripeptide-1": "peptides",
    "palmitoyl tetrapeptide-7": "peptides",
    "copper peptide": "peptides",
}

def normalize_ingredient_name(name: str) -> str:
    cleaned = name.lower().strip()

    cleaned = cleaned.replace("-", " ")
    cleaned = re.sub(r"\s+", " ", cleaned)

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
