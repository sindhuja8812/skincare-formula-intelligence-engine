import pytest

from utils.summary_generator import generate_formula_summary, get_final_recommendation


class TestGenerateFormulaSummary:

    def _base_call(self, score=87.8, risk="Low", skin="oily"):
        return generate_formula_summary(
            skin_type=skin,
            compatibility_score=score,
            risk_level=risk,
            benefits=["Oil Control", "Brightening", "Acne Support"],
            concerns=[],
            strengths=["Niacinamide", "Zinc Pca", "Salicylic Acid"],
            weaknesses=[],
        )

    def test_returns_string(self):
        assert isinstance(self._base_call(), str)

    def test_contains_score(self):
        result = self._base_call(score=87.8)
        assert "87.8" in result

    def test_contains_skin_type(self):
        result = self._base_call(skin="oily")
        assert "oily" in result.lower()

    def test_excellent_band_opening(self):
        result = self._base_call(score=90)
        assert "Excellent" in result

    def test_good_band_opening(self):
        result = generate_formula_summary(
            skin_type="dry", compatibility_score=65, risk_level="Moderate",
            benefits=["Hydration"], concerns=["Dryness Risk"],
            strengths=["Glycerin"], weaknesses=["Salicylic Acid"],
        )
        assert "Good" in result

    def test_caution_band_opening(self):
        result = generate_formula_summary(
            skin_type="dry", compatibility_score=50, risk_level="High",
            benefits=[], concerns=["Irritation Risk"],
            strengths=[], weaknesses=["Fragrance"],
        )
        assert "Limited" in result

    def test_low_risk_bullet(self):
        result = self._base_call(risk="Low")
        assert "Low irritation risk" in result

    def test_moderate_risk_bullet(self):
        result = self._base_call(risk="Moderate")
        assert "patch testing" in result.lower()

    def test_high_risk_bullet(self):
        result = self._base_call(risk="High")
        assert "caution" in result.lower()

    def test_no_concerns_bullet(self):
        result = self._base_call()
        assert "No major concerns" in result

    def test_strengths_listed(self):
        result = self._base_call()
        assert "Niacinamide" in result

    def test_bullet_format(self):
        result = self._base_call()
        lines = result.strip().split("\n")
        for line in lines:
            assert line.startswith("•")


class TestGetFinalRecommendation:

    def test_high_score(self):
        assert get_final_recommendation(85) == "Excellent Match"

    def test_low_score(self):
        assert get_final_recommendation(20) == "Not Recommended"