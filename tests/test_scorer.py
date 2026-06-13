
import pytest
from utils.scorer import (
    get_formula_verdict,
    calculate_coverage,
    calculate_skin_match_score,
    calculate_overall_formula_score,
    REALISM_FACTOR,
    MAX_SCORE,
)


# Fixtures — minimal ingredient dicts that mirror CSV rows

@pytest.fixture
def high_score_ingredients():
    """All scores 10/10 — ideal formula."""
    return [
        {
            "ingredient": "niacinamide",
            "sensitive_score": 8, "oily_score": 10, "dry_score": 8,
            "combination_score": 9, "normal_score": 9,
        },
        {
            "ingredient": "glycerin",
            "sensitive_score": 10, "oily_score": 8, "dry_score": 10,
            "combination_score": 9, "normal_score": 9,
        },
    ]

@pytest.fixture
def low_score_ingredients():
    """Low scores — poor formula."""
    return [
        {
            "ingredient": "fragrance",
            "sensitive_score": 1, "oily_score": 5, "dry_score": 5,
            "combination_score": 5, "normal_score": 5,
        },
        {
            "ingredient": "alcohol denat",
            "sensitive_score": 1, "oily_score": 7, "dry_score": 2,
            "combination_score": 4, "normal_score": 5,
        },
    ]

@pytest.fixture
def single_ingredient():
    return [
        {
            "ingredient": "hyaluronic acid",
            "sensitive_score": 10, "oily_score": 9, "dry_score": 10,
            "combination_score": 10, "normal_score": 10,
        }
    ]


# get_formula_verdict

class TestGetFormulaVerdict:

    def test_excellent_match(self):
        assert get_formula_verdict(85) == "Excellent Match"

    def test_very_good_match(self):
        assert get_formula_verdict(75) == "Very Good Match"

    def test_good_match(self):
        assert get_formula_verdict(65) == "Good Match"

    def test_use_with_caution(self):
        assert get_formula_verdict(50) == "Use With Caution"

    def test_not_recommended(self):
        assert get_formula_verdict(10) == "Not Recommended"

    def test_exact_boundary_82(self):
        assert get_formula_verdict(82) == "Excellent Match"

    def test_exact_boundary_72(self):
        assert get_formula_verdict(72) == "Very Good Match"

    def test_exact_boundary_62(self):
        assert get_formula_verdict(62) == "Good Match"

    def test_exact_boundary_48(self):
        assert get_formula_verdict(48) == "Use With Caution"

    def test_zero_score(self):
        assert get_formula_verdict(0) == "Not Recommended"


# calculate_coverage

class TestCalculateCoverage:

    def test_full_coverage(self):
        result = calculate_coverage([{}, {}, {}], 3)
        assert result["coverage"] == 100.0
        assert result["recognized_ingredients"] == 3
        assert result["total_ingredients"] == 3

    def test_partial_coverage(self):
        result = calculate_coverage([{}, {}], 4)
        assert result["coverage"] == 50.0

    def test_zero_total(self):
        result = calculate_coverage([], 0)
        assert result["coverage"] == 0.0

    def test_no_matches(self):
        result = calculate_coverage([], 5)
        assert result["coverage"] == 0.0
        assert result["recognized_ingredients"] == 0


# calculate_skin_match_score

class TestCalculateSkinMatchScore:

    def test_oily_skin_score_structure(self, high_score_ingredients):
        result = calculate_skin_match_score(high_score_ingredients, "oily", 2)
        assert "score" in result
        assert "verdict" in result
        assert "coverage" in result
        assert "explanation" in result

    def test_score_does_not_exceed_max(self, high_score_ingredients):
        result = calculate_skin_match_score(high_score_ingredients, "oily", 2)
        assert result["score"] <= MAX_SCORE

    def test_realism_factor_applied(self, single_ingredient):
        result = calculate_skin_match_score(single_ingredient, "oily", 1)
        # oily_score=9 → raw=90 → 90*0.9 = 81.0
        assert result["score"] == pytest.approx(81.0, abs=0.5)

    def test_low_score_formula(self, low_score_ingredients):
        result = calculate_skin_match_score(low_score_ingredients, "sensitive", 2)
        assert result["score"] < 20

    def test_invalid_skin_type_raises(self, high_score_ingredients):
        with pytest.raises(ValueError, match="Unknown skin type"):
            calculate_skin_match_score(high_score_ingredients, "alien", 2)

    def test_empty_ingredients_raises(self):
        with pytest.raises(ValueError, match="must not be empty"):
            calculate_skin_match_score([], "oily", 0)

    def test_all_skin_types_accepted(self, high_score_ingredients):
        for skin in ["sensitive", "oily", "dry", "combination", "normal"]:
            result = calculate_skin_match_score(high_score_ingredients, skin, 2)
            assert result["score"] > 0

    def test_coverage_reflects_total(self, high_score_ingredients):
        result = calculate_skin_match_score(high_score_ingredients, "oily", 10)
        assert result["coverage"]["total_ingredients"] == 10
        assert result["coverage"]["recognized_ingredients"] == 2



# calculate_overall_formula_score


class TestCalculateOverallFormulaScore:

    def test_returns_score(self, high_score_ingredients):
        result = calculate_overall_formula_score(high_score_ingredients, 2)
        assert "score" in result
        assert result["score"] > 0

    def test_score_capped_at_max(self, high_score_ingredients):
        result = calculate_overall_formula_score(high_score_ingredients, 2)
        assert result["score"] <= MAX_SCORE

    def test_low_formula_lower_than_high(self, high_score_ingredients, low_score_ingredients):
        high_result = calculate_overall_formula_score(high_score_ingredients, 2)
        low_result  = calculate_overall_formula_score(low_score_ingredients, 2)
        assert high_result["score"] > low_result["score"]

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="must not be empty"):
            calculate_overall_formula_score([], 0)

    def test_single_ingredient(self, single_ingredient):
        result = calculate_overall_formula_score(single_ingredient, 1)
        assert result["score"] > 0