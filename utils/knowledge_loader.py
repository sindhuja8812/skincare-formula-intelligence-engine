
import pandas as pd
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "ingredient_knowledge.csv"


def load_knowledge_base() -> pd.DataFrame:
  
    df = pd.read_csv(DATA_PATH)

    df["ingredient"] = df["ingredient"].str.lower().str.strip()
    df["benefits"] = df["benefits"].fillna("None")
    df["concerns"] = df["concerns"].fillna("None")
    df = df.drop_duplicates(subset="ingredient")

    return df.reset_index(drop=True)


def find_ingredient(name: str, df: pd.DataFrame) -> dict | None:
   
    normalized = name.lower().strip()
    match = df[df["ingredient"] == normalized]

    if match.empty:
        return None

    return match.iloc[0].to_dict()


def get_all_ingredients(df: pd.DataFrame) -> set[str]:

    return set(df["ingredient"].tolist())



