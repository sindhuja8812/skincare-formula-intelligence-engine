import re
from typing import List

# ---------------------------------------------------------------------------
# Synonym mapping — maps common aliases to EXACT knowledge-base names
# (after load_knowledge_base lowercases them)
#
# Rule: every value on the right must exactly match a lowercased CSV ingredient.
# ---------------------------------------------------------------------------
SYNONYMS: dict[str, str] = {

    # ── Water ────────────────────────────────────────────────────────────────
    "aqua":                             "water",

    # ── Hyaluronic Acid ──────────────────────────────────────────────────────
    "sodium hyaluronate":               "hyaluronic acid",
    "hydrolyzed hyaluronic acid":       "hyaluronic acid",
    "ha":                               "hyaluronic acid",

    # ── Aloe ─────────────────────────────────────────────────────────────────
    "aloe barbadensis leaf juice":      "aloe vera",
    "aloe barbadensis":                 "aloe vera",
    "aloe":                             "aloe vera",

    # ── Vitamin E ────────────────────────────────────────────────────────────
    # CSV name (lowercased): "vitamin e (tocopherol)"
    "vitamin e":                        "vitamin e (tocopherol)",
    "tocopherol":                       "vitamin e (tocopherol)",
    "tocopheryl acetate":               "tocopheryl acetate",   # own CSV row
    "alpha tocopherol":                 "vitamin e (tocopherol)",
    "d-alpha tocopherol":               "vitamin e (tocopherol)",

    # ── Vitamin C ────────────────────────────────────────────────────────────
    # CSV name (lowercased): "vitamin c (l-ascorbic acid)"
    "vitamin c":                        "vitamin c (l-ascorbic acid)",
    "ascorbic acid":                    "vitamin c (l-ascorbic acid)",
    "l-ascorbic acid":                  "vitamin c (l-ascorbic acid)",
    "ascorbyl glucoside":               "ascorbyl glucoside",   # own CSV row
    "sodium ascorbyl phosphate":        "sodium ascorbyl phosphate",
    "ascorbyl tetraisopalmitate":       "ascorbyl tetraisopalmitate",
    "ethyl ascorbic acid":              "ethyl ascorbic acid",
    "3-o-ethyl ascorbic acid":          "ethyl ascorbic acid",
    "magnesium ascorbyl phosphate":     "vitamin c (l-ascorbic acid)",

    # ── Ceramides ────────────────────────────────────────────────────────────
    # Each ceramide has its own CSV row; "ceramide" alone → ceramide np (most common)
    "ceramide":                         "ceramide np",
    "ceramide np":                      "ceramide np",
    "ceramide ap":                      "ceramide ap",
    "ceramide eop":                     "ceramide eop",
    "ceramide ns":                      "ceramide ns",
    "ceramide as":                      "ceramide as",

    # ── Peptides ─────────────────────────────────────────────────────────────
    # CSV name: "peptide complex"
    "peptides":                         "peptide complex",
    "peptide":                          "peptide complex",
    "acetyl hexapeptide-8":             "acetyl hexapeptide-3",   # common rename
    "palmitoyl tripeptide-1":           "palmitoyl tripeptide-5",
    "palmitoyl tetrapeptide-7":         "peptide complex",
    "copper peptide":                   "copper peptide",
    "matrixyl":                         "matrixyl 3000",

    # ── Centella / Cica ───────────────────────────────────────────────────────
    "centella asiatica":                "centella asiatica extract",
    "centella":                         "centella asiatica extract",
    "cica":                             "centella asiatica extract",
    "gotu kola":                        "centella asiatica extract",
    "tiger grass":                      "centella asiatica extract",

    # ── Green Tea ────────────────────────────────────────────────────────────
    "camellia sinensis leaf extract":   "green tea extract",
    "green tea":                        "green tea extract",
    "egcg":                             "epigallocatechin gallate (egcg)",

    # ── Tea Tree ─────────────────────────────────────────────────────────────
    "melaleuca alternifolia leaf oil":  "tea tree oil",
    "tea tree":                         "tea tree oil",

    # ── Niacinamide ──────────────────────────────────────────────────────────
    "nicotinamide":                     "niacinamide",
    "vitamin b3":                       "niacinamide",

    # ── Beta Glucan ──────────────────────────────────────────────────────────
    "beta-glucan":                      "beta glucan",
    "β-glucan":                         "beta glucan",

    # ── Salicylic Acid ───────────────────────────────────────────────────────
    "bha":                              "salicylic acid",
    "beta hydroxy acid":                "salicylic acid",

    # ── AHAs ─────────────────────────────────────────────────────────────────
    "aha":                              "glycolic acid",
    "glycolic":                         "glycolic acid",
    "lactic":                           "lactic acid",

    # ── Retinol / Retinoids ──────────────────────────────────────────────────
    "retinyl palmitate":                "retinyl palmitate",
    "retinal":                          "retinal",
    "retinaldehyde":                    "retinal",
    "vitamin a":                        "retinol",

    # ── Panthenol ────────────────────────────────────────────────────────────
    "d-panthenol":                      "panthenol",
    "provitamin b5":                    "panthenol",
    "vitamin b5":                       "panthenol",

    # ── Alpha Arbutin ────────────────────────────────────────────────────────
    "arbutin":                          "alpha arbutin",

    # ── Licorice ─────────────────────────────────────────────────────────────
    "glycyrrhiza glabra root extract":  "licorice root extract",
    "licorice":                         "licorice root extract",
    "licorice extract":                 "licorice root extract",

    # ── Squalane ─────────────────────────────────────────────────────────────
    "olive squalane":                   "squalane",
    "sugarcane squalane":               "squalane",

    # ── Shea Butter ──────────────────────────────────────────────────────────
    "butyrospermum parkii butter":      "shea butter",
    "shea":                             "shea butter",

    # ── Fragrance / Irritants ────────────────────────────────────────────────
    "parfum":                           "fragrance",
    "perfume":                          "fragrance",

    # ── Alcohol ──────────────────────────────────────────────────────────────
    "alcohol denat.":                   "alcohol denat",
    "denatured alcohol":                "alcohol denat",
    "sd alcohol":                       "alcohol denat",
    "isopropyl alcohol":                "alcohol denat",

    # ── Zinc ─────────────────────────────────────────────────────────────────
    "zinc":                             "zinc pca",

    # ── Hyaluronic Acid forms ────────────────────────────────────────────────
    "sodium pca":                       "sodium pca",
}


def normalize_ingredient_name(name: str) -> str:
    cleaned = name.lower().strip()
    cleaned = re.sub(r"\s+", " ", cleaned)          # collapse internal spaces
    return SYNONYMS.get(cleaned, cleaned)


def parse_ingredients(raw_text: str) -> List[str]:
    """Split on comma / semicolon / newline, normalize, deduplicate."""
    tokens = re.split(r"[,;\n]+", raw_text)

    seen: set[str] = set()
    result: List[str] = []

    for token in tokens:
        normalized = normalize_ingredient_name(token)
        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(normalized)

    return result