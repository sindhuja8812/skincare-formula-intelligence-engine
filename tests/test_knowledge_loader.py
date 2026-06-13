
import pytest
import pandas as pd
from utils.knowledge_loader import load_knowledge_base, find_ingredient, get_all_ingredients

# Fixtures

@pytest.fixture(scope="module")
def kb():
    """Load the knowledge base once for all tests in this module."""
    return load_knowledge_base()


# load_knowledge_base

class TestLoadKnowledgeBase:

    def test_returns_dataframe(self, kb):
        assert isinstance(kb, pd.DataFrame)

    def test_not_empty(self, kb):
        assert len(kb) > 0

    def test_ingredient_column_exists(self, kb):
        assert "ingredient" in kb.columns

    def test_ingredients_are_lowercase(self, kb):
        for name in kb["ingredient"]:
            assert name == name.lower(), f"Not lowercase: {name}"

    def test_ingredients_are_stripped(self, kb):
        for name in kb["ingredient"]:
            assert name == name.strip(), f"Has leading/trailing space: {name}"

    def test_no_duplicate_ingredients(self, kb):
        assert kb["ingredient"].duplicated().sum() == 0

    def test_benefits_column_no_nulls(self, kb):
        assert kb["benefits"].isnull().sum() == 0

    def test_concerns_column_no_nulls(self, kb):
        assert kb["concerns"].isnull().sum() == 0

    def test_required_score_columns_exist(self, kb):
        for col in ["sensitive_score", "oily_score", "dry_score",
                    "combination_score", "normal_score"]:
            assert col in kb.columns, f"Missing column: {col}"

    def test_required_risk_columns_exist(self, kb):
        for col in ["sensitive_risk", "oily_risk", "dry_risk",
                    "combination_risk", "normal_risk", "risk_level"]:
            assert col in kb.columns, f"Missing column: {col}"

    def test_index_is_reset(self, kb):
        assert list(kb.index) == list(range(len(kb)))

    def test_known_ingredient_present(self, kb):
        assert "niacinamide" in kb["ingredient"].values

    def test_scores_within_range(self, kb):
        for col in ["sensitive_score", "oily_score", "dry_score",
                    "combination_score", "normal_score"]:
            assert kb[col].between(0, 10).all(), f"Score out of range in {col}"


# find_ingredient

class TestFindIngredient:

    def test_returns_dict_for_known(self, kb):
        result = find_ingredient("niacinamide", kb)
        assert isinstance(result, dict)

    def test_returns_none_for_unknown(self, kb):
        result = find_ingredient("unicorn dust", kb)
        assert result is None

    def test_case_insensitive_lookup(self, kb):
        result = find_ingredient("GLYCERIN", kb)
        assert result is not None

    def test_whitespace_trimmed_lookup(self, kb):
        result = find_ingredient("  glycerin  ", kb)
        assert result is not None

    def test_correct_ingredient_returned(self, kb):
        result = find_ingredient("glycerin", kb)
        assert result["ingredient"] == "glycerin"

    def test_result_contains_score_keys(self, kb):
        result = find_ingredient("niacinamide", kb)
        assert "oily_score" in result
        assert "sensitive_score" in result

    def test_result_contains_risk_key(self, kb):
        result = find_ingredient("niacinamide", kb)
        assert "risk_level" in result

    def test_result_contains_benefits(self, kb):
        result = find_ingredient("niacinamide", kb)
        assert "benefits" in result
        assert result["benefits"] != ""

    def test_empty_string_returns_none(self, kb):
        result = find_ingredient("", kb)
        assert result is None

    def test_partial_name_returns_none(self, kb):
        # "niacin" is not a full match — should return None
        result = find_ingredient("niacin", kb)
        assert result is None

    def test_salicylic_acid_found(self, kb):
        result = find_ingredient("salicylic acid", kb)
        assert result is not None
        assert result["oily_score"] == 10

    def test_fragrance_found_and_high_risk(self, kb):
        result = find_ingredient("fragrance", kb)
        assert result is not None
        assert result["risk_level"] == "High"


# get_all_ingredients

class TestGetAllIngredients:

    def test_returns_set(self, kb):
        result = get_all_ingredients(kb)
        assert isinstance(result, set)

    def test_not_empty(self, kb):
        result = get_all_ingredients(kb)
        assert len(result) > 0

    def test_known_ingredient_in_set(self, kb):
        result = get_all_ingredients(kb)
        assert "niacinamide" in result

    def test_all_lowercase(self, kb):
        result = get_all_ingredients(kb)
        for name in result:
            assert name == name.lower(), f"Not lowercase: {name}"

    def test_length_matches_dataframe(self, kb):
        result = get_all_ingredients(kb)
        assert len(result) == len(kb)

    def test_no_duplicates_in_set(self, kb):
        result = get_all_ingredients(kb)
        # Sets are inherently duplicate-free; just confirm count matches unique count
        assert len(result) == len(set(result))