import pytest
from utils.recommendations import (
    generate_addition_recommendations,
    generate_avoid_recommendations,
    get_formula_strengths,
    get_formula_weaknesses,
    PREFERRED_BY_SKIN_TYPE,
)


# Fixtures


@pytest.fixture
def oily_formula():
    """Formula that already has niacinamide and zinc pca for oily skin."""
    return [
        {"ingredient": "niacinamide",    "oily_score": 10, "sensitive_score": 8, "dry_score": 8, "combination_score": 9, "normal_score": 9, "risk_level": "Low"},
        {"ingredient": "zinc pca",       "oily_score": 10, "sensitive_score": 8, "dry_score": 6, "combination_score": 9, "normal_score": 8, "risk_level": "Low"},
    ]

@pytest.fixture
def empty_formula():
    return []

@pytest.fixture
def fragrance_formula():
    return [
        {"ingredient": "fragrance",    "oily_score": 5, "sensitive_score": 1, "dry_score": 5, "combination_score": 5, "normal_score": 5, "risk_level": "High"},
        {"ingredient": "alcohol denat","oily_score": 7, "sensitive_score": 1, "dry_score": 2, "combination_score": 4, "normal_score": 5, "risk_level": "High"},
    ]

@pytest.fixture
def mixed_score_ingredients():
    return [
        {"ingredient": "niacinamide",   "oily_score": 10, "sensitive_score": 8, "dry_score": 8, "combination_score": 9, "normal_score": 9, "risk_level": "Low"},
        {"ingredient": "salicylic acid","oily_score": 10, "sensitive_score": 3, "dry_score": 4, "combination_score": 7, "normal_score": 7, "risk_level": "Moderate"},
        {"ingredient": "glycerin",      "oily_score": 8,  "sensitive_score": 10,"dry_score": 10,"combination_score": 9, "normal_score": 9, "risk_level": "Low"},
    ]


# generate_addition_recommendations

class TestGenerateAdditionRecommendations:

    def test_missing_preferred_ingredients_recommended(self, empty_formula):
        # Empty formula → all preferred for oily recommended
        result = generate_addition_recommendations("oily", empty_formula)
        assert len(result) > 0

    def test_present_ingredients_not_recommended(self, oily_formula):
        result = generate_addition_recommendations("oily", oily_formula)
        present_lower = {r.lower() for r in result}
        assert "niacinamide" not in present_lower
        assert "zinc pca" not in present_lower

    def test_returns_title_case(self, empty_formula):
        result = generate_addition_recommendations("oily", empty_formula)
        for name in result:
            assert name == name.title() or name[0].isupper()

    def test_max_5_recommendations(self, empty_formula):
        result = generate_addition_recommendations("dry", empty_formula)
        assert len(result) <= 5

    def test_invalid_skin_type_raises(self, empty_formula):
        with pytest.raises(ValueError, match="Unknown skin type"):
            generate_addition_recommendations("alien", empty_formula)

    def test_full_formula_returns_empty(self):
        # Formula already contains all preferred oily ingredients
        full = [{"ingredient": name} for name in PREFERRED_BY_SKIN_TYPE["oily"]]
        result = generate_addition_recommendations("oily", full)
        assert result == []

    def test_all_skin_types_valid(self, empty_formula):
        for skin in ["sensitive", "oily", "dry", "combination", "normal"]:
            result = generate_addition_recommendations(skin, empty_formula)
            assert isinstance(result, list)


# generate_avoid_recommendations

class TestGenerateAvoidRecommendations:

    def test_fragrance_flagged_for_sensitive(self, fragrance_formula):
        result = generate_avoid_recommendations("sensitive", fragrance_formula)
        assert "Fragrance" in result

    def test_safe_formula_returns_empty(self, oily_formula):
        result = generate_avoid_recommendations("oily", oily_formula)
        assert result == []

    def test_invalid_skin_type_raises(self, oily_formula):
        with pytest.raises(ValueError, match="Unknown skin type"):
            generate_avoid_recommendations("alien", oily_formula)

    def test_normal_skin_no_avoids(self, fragrance_formula):
        # Normal has empty avoid list
        result = generate_avoid_recommendations("normal", fragrance_formula)
        assert result == []


# get_formula_strengths

class TestGetFormulaStrengths:

    def test_returns_list(self, mixed_score_ingredients):
        result = get_formula_strengths(mixed_score_ingredients, "oily")
        assert isinstance(result, list)

    def test_highest_score_first(self, mixed_score_ingredients):
        result = get_formula_strengths(mixed_score_ingredients, "oily")
        # niacinamide and salicylic acid both 10 for oily — either can be first
        assert result[0].lower() in ["niacinamide", "salicylic acid"]

    def test_max_5_returned(self, mixed_score_ingredients):
        result = get_formula_strengths(mixed_score_ingredients, "oily")
        assert len(result) <= 5

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="must not be empty"):
            get_formula_strengths([], "oily")

    def test_invalid_skin_type_raises(self, mixed_score_ingredients):
        with pytest.raises(ValueError, match="Unknown skin type"):
            get_formula_strengths(mixed_score_ingredients, "alien")


# get_formula_weaknesses

class TestGetFormulaWeaknesses:

    def test_moderate_risk_flagged(self, mixed_score_ingredients):
        result = get_formula_weaknesses(mixed_score_ingredients, "oily")
        assert "Salicylic Acid" in result

    def test_low_score_flagged(self):
        ings = [
            {"ingredient": "alcohol denat", "oily_score": 7, "risk_level": "High",
             "sensitive_score": 1, "dry_score": 2, "combination_score": 4, "normal_score": 5},
        ]
        result = get_formula_weaknesses(ings, "oily")
        assert "Alcohol Denat" in result

    def test_all_good_ingredients_returns_empty(self):
        ings = [
            {"ingredient": "glycerin",    "oily_score": 8,  "risk_level": "Low",
             "sensitive_score": 10, "dry_score": 10, "combination_score": 9, "normal_score": 9},
            {"ingredient": "niacinamide", "oily_score": 10, "risk_level": "Low",
             "sensitive_score": 8,  "dry_score": 8,  "combination_score": 9, "normal_score": 9},
        ]
        result = get_formula_weaknesses(ings, "oily")
        assert result == []

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="must not be empty"):
            get_formula_weaknesses([], "oily")

