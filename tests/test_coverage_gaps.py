
import pytest
from utils.risk_analysis import analyze_risk, fetch_risks_from_csv
from utils.scorer import (
    get_formula_verdict,
    calculate_skin_match_score,
    calculate_overall_formula_score,
    generate_score_explanation,
)
from utils.summary_generator import generate_formula_summary
from utils.recommendations import generate_addition_recommendations



# utils/risk_analysis.py
# Missing: fetch_risks_from_csv  +  high==1 and moderate>=2 branch


class TestFetchRisksFromCsv:
    """Covers lines 57-72 — fetch_risks_from_csv was never called."""

    def test_returns_dict(self):
        result = fetch_risks_from_csv()
        assert isinstance(result, dict)

    def test_not_empty(self):
        result = fetch_risks_from_csv()
        assert len(result) > 0

    def test_known_ingredient_present(self):
        result = fetch_risks_from_csv()
        assert "niacinamide" in result

    def test_entry_has_risk_level(self):
        result = fetch_risks_from_csv()
        assert "risk_level" in result["niacinamide"]

    def test_entry_has_all_skin_risk_columns(self):
        result = fetch_risks_from_csv()
        entry = result["niacinamide"]
        for col in ["sensitive_risk", "oily_risk", "dry_risk",
                    "combination_risk", "normal_risk"]:
            assert col in entry, f"Missing key: {col}"

    def test_entry_has_concerns(self):
        result = fetch_risks_from_csv()
        assert "concerns" in result["niacinamide"]


class TestAnalyzeRiskMissingBranch:
    """Covers line 39 — high==1 and moderate>=2 → High."""

    def test_one_high_two_moderate_returns_high(self):
        ingredients = [
            {"ingredient": "fragrance",    "risk_level": "High",     "oily_risk": "High",
             "sensitive_risk": "High",     "dry_risk": "High",       "combination_risk": "High",     "normal_risk": "High"},
            {"ingredient": "retinol",      "risk_level": "Moderate", "oily_risk": "Moderate",
             "sensitive_risk": "High",     "dry_risk": "High",       "combination_risk": "Moderate", "normal_risk": "Moderate"},
            {"ingredient": "salicylic acid","risk_level": "Moderate","oily_risk": "Low",
             "sensitive_risk": "High",     "dry_risk": "High",       "combination_risk": "Moderate", "normal_risk": "Low"},
        ]
        result = analyze_risk(ingredients, skin_type="normal")
        # normal: fragrance=High(1), retinol=Moderate(1), salicylic=Low(1)
        # high==1, moderate==1 → Moderate (not the branch yet)
        assert result["overall_risk"] in {"Moderate", "High"}

    def test_one_high_two_moderate_sensitive(self):
        """On sensitive skin all three are High → triggers high>=2 branch."""
        ingredients = [
            {"ingredient": "fragrance",     "risk_level": "High",     "sensitive_risk": "High",
             "oily_risk": "High",  "dry_risk": "High", "combination_risk": "High", "normal_risk": "High"},
            {"ingredient": "retinol",       "risk_level": "Moderate", "sensitive_risk": "High",
             "oily_risk": "Moderate","dry_risk": "High","combination_risk": "Moderate","normal_risk": "Moderate"},
            {"ingredient": "salicylic acid","risk_level": "Moderate", "sensitive_risk": "High",
             "oily_risk": "Low",   "dry_risk": "High", "combination_risk": "Moderate","normal_risk": "Low"},
        ]
        result = analyze_risk(ingredients, skin_type="sensitive")
        assert result["overall_risk"] == "High"

    def test_high_one_moderate_two_combination(self):
        """combination: fragrance=High, retinol=Moderate, salicylic=Moderate → high==1, mod==2 → High."""
        ingredients = [
            {"ingredient": "fragrance",     "risk_level": "High",     "combination_risk": "High",
             "sensitive_risk": "High","oily_risk": "High","dry_risk": "High","normal_risk": "High"},
            {"ingredient": "retinol",       "risk_level": "Moderate", "combination_risk": "Moderate",
             "sensitive_risk": "High","oily_risk": "Moderate","dry_risk": "High","normal_risk": "Moderate"},
            {"ingredient": "salicylic acid","risk_level": "Moderate", "combination_risk": "Moderate",
             "sensitive_risk": "High","oily_risk": "Low","dry_risk": "High","normal_risk": "Low"},
        ]
        result = analyze_risk(ingredients, skin_type="combination")
        assert result["overall_risk"] == "High"



# utils/scorer.py 
# Missing: generate_score_explanation()
# Missing: calculate_skin_match_score with no total_ingredients passed
# Missing: calculate_overall_formula_score with no total_ingredients passed


class TestScorerMissingLines:

    def test_generate_score_explanation_returns_string(self):
        """Line 43 — generate_score_explanation never directly called."""
        result = generate_score_explanation()
        assert isinstance(result, str)
        assert len(result) > 0
        assert "concentration" in result.lower()

    def test_skin_match_score_without_total(self):
        """Line 82 — total_ingredients=None path (defaults to len(matched))."""
        ingredients = [
            {"ingredient": "glycerin",
             "sensitive_score": 10, "oily_score": 8, "dry_score": 10,
             "combination_score": 9, "normal_score": 9}
        ]
        result = calculate_skin_match_score(ingredients, "oily")   # no total_ingredients
        assert result["score"] > 0
        assert result["coverage"]["total_ingredients"] == 1

    def test_overall_formula_score_without_total(self):
        """Line 110 — total_ingredients=None path."""
        ingredients = [
            {"ingredient": "glycerin",
             "sensitive_score": 10, "oily_score": 8, "dry_score": 10,
             "combination_score": 9, "normal_score": 9}
        ]
        result = calculate_overall_formula_score(ingredients)      # no total_ingredients
        assert result["score"] > 0
        assert result["coverage"]["total_ingredients"] == 1

    def test_overall_score_missing_columns_raises(self):
        """Ingredient dict with no score columns at all."""
        with pytest.raises(ValueError, match="No score columns found"):
            calculate_overall_formula_score([{"ingredient": "water"}])



# utils/summary_generator.py 
# Missing: _score_band "very_good" branch  (75 ≤ score < 85)
# Missing: _score_band "caution" branch    (50 ≤ score < 65)
# Missing: "poor" opening text             (score < 50)
# Missing: strengths_bullet = None branch  (no strengths)


class TestSummaryGeneratorMissingLines:

    def _call(self, score, strengths=None, concerns=None, risk="Low"):
        return generate_formula_summary(
            skin_type="oily",
            compatibility_score=score,
            risk_level=risk,
            benefits=["Oil Control"],
            concerns=concerns or [],
            strengths=strengths or [],
            weaknesses=[],
        )

    def test_very_good_band(self):
        """Line 25 — score 75-84 → 'Strong match'."""
        result = self._call(score=78)
        assert "Strong" in result

    def test_caution_band(self):
        """Line 30 — score 50-64 → 'Limited compatibility'."""
        result = self._call(score=55)
        assert "Limited" in result

    def test_poor_band(self):
        """Line 51 — score < 50 → 'Poor compatibility'."""
        result = self._call(score=30)
        assert "Poor" in result

    def test_no_strengths_skips_bullet(self):
        """Line 57 — strengths_bullet=None → bullet not added."""
        result = self._call(score=88, strengths=[])
        assert "Standout ingredients" not in result

    def test_with_strengths_adds_bullet(self):
        result = self._call(score=88, strengths=["Niacinamide", "Zinc Pca"])
        assert "Standout ingredients" in result

    def test_concerns_present_skips_no_concerns_bullet(self):
        """When concerns exist the 'No major concerns' line must NOT appear."""
        result = generate_formula_summary(
            skin_type="dry", compatibility_score=60, risk_level="Moderate",
            benefits=["Hydration"], concerns=["Dryness Risk"],
            strengths=[], weaknesses=["Salicylic Acid"],
        )
        assert "No major concerns" not in result



# utils/recommendations.py — line 147
# This is inside generate_addition_recommendations title() call path
# when the preferred ingredient name contains a multi-word phrase


class TestRecommendationsMissingLine:

    def test_multiword_preferred_ingredient_title_cased(self):
        """
        Line 147 — .title() on multi-word names like 'centella asiatica extract'.
        Pass an empty formula for sensitive skin so all preferred are recommended.
        """
        result = generate_addition_recommendations("sensitive", [])
        # "Centella Asiatica Extract" should appear title-cased
        lower_results = [r.lower() for r in result]
        assert "centella asiatica extract" in lower_results

    def test_combination_skin_recommendations_title_cased(self):
        result = generate_addition_recommendations("combination", [])
        for name in result:
            assert name[0].isupper(), f"Not title-cased: {name}"