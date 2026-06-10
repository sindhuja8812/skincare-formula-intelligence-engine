"""
knowledge_loader.py

Handles loading and querying the ingredient knowledge base CSV.
"""

import pandas as pd
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "ingredient_knowledge.csv"


def load_knowledge_base() -> pd.DataFrame:
    """
    Load the ingredient knowledge base from CSV.

    Cleans the DataFrame by:
    - Lowercasing and stripping whitespace from ingredient names
    - Filling missing benefits/concerns with 'None'
    - Removing duplicate ingredient entries

    Returns:
        pd.DataFrame: Cleaned ingredient knowledge base.
    """
    df = pd.read_csv(DATA_PATH)

    df["ingredient"] = df["ingredient"].str.lower().str.strip()
    df["benefits"] = df["benefits"].fillna("None")
    df["concerns"] = df["concerns"].fillna("None")
    df = df.drop_duplicates(subset="ingredient")

    return df.reset_index(drop=True)


def find_ingredient(name: str, df: pd.DataFrame) -> dict | None:
    """
    Look up a single ingredient by name in the knowledge base.

    Args:
        name: Ingredient name to search for (case-insensitive).
        df:   Loaded knowledge base DataFrame.

    Returns:
        dict: Full ingredient row as a dictionary, or None if not found.
    """
    normalized = name.lower().strip()
    match = df[df["ingredient"] == normalized]

    if match.empty:
        return None

    return match.iloc[0].to_dict()


def get_all_ingredients(df: pd.DataFrame) -> set[str]:
    """
    Return a set of all ingredient names in the knowledge base.

    Args:
        df: Loaded knowledge base DataFrame.

    Returns:
        set[str]: All ingredient names (already normalized to lowercase).
    """
    return set(df["ingredient"].tolist())


# ---------------------------------------------------------------------------
# Test section
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    kb = load_knowledge_base()

    print(f"[INFO] Loaded {len(kb)} ingredients.\n")

    # Test Case 3 — search for 'ceramide np'
    result = find_ingredient("ceramide np", kb)
    assert result is not None, "FAIL: 'ceramide np' not found"
    print(f"[PASS] find_ingredient('ceramide np'):")
    for k, v in result.items():
        print(f"  {k}: {v}")

    # Confirm get_all_ingredients returns a set
    all_ingredients = get_all_ingredients(kb)
    assert isinstance(all_ingredients, set), "FAIL: expected set"
    assert "glycerin" in all_ingredients, "FAIL: 'glycerin' missing from set"
    print(f"\n[PASS] get_all_ingredients() returned {len(all_ingredients)} ingredients.")

    # Edge case — unknown ingredient
    missing = find_ingredient("unknown ingredient xyz", kb)
    assert missing is None, "FAIL: expected None for unknown ingredient"
    print("\n[PASS] find_ingredient returns None for unknown ingredient.")
