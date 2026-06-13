
import pytest
from utils.risk_analysis import analyze_risk



# Fixtures


@pytest.fixture
def all_low_risk():
    return [
        {"ingredient": "glycerin",        "risk_level": "Low",  "oily_risk": "Low",  "sensitive_risk": "Low",  "dry_risk": "Low",  "combination_risk": "Low",  "normal_risk": "Low"},
        {"ingredient": "niacinamide",      "risk_level": "Low",  "oily_risk": "Low",  "sensitive_risk": "Low",  "dry_risk": "Low",  "combination_risk": "Low",  "normal_risk": "Low"},
        {"ingredient": "hyaluronic acid",  "risk_level": "Low",  "oily_risk": "Low",  "sensitive_risk": "Low",  "dry_risk": "Low",  "combination_risk": "Low",  "normal_risk": "Low"},
    ]

@pytest.fixture
def one_high_risk():
    return [
        {"ingredient": "glycerin",   "risk_level": "Low",  "oily_risk": "Low",  "sensitive_risk": "Low",      "dry_risk": "Low",  "combination_risk": "Low",  "normal_risk": "Low"},
        {"ingredient": "salicylic acid", "risk_level": "Moderate", "oily_risk": "Low", "sensitive_risk": "High", "dry_risk": "High", "combination_risk": "Moderate", "normal_risk": "Low"},
    ]

@pytest.fixture
def two_high_risk():
    return [
        {"ingredient": "fragrance",    "risk_level": "High", "oily_risk": "High",  "sensitive_risk": "High", "dry_risk": "High", "combination_risk": "High", "normal_risk": "High"},
        {"ingredient": "alcohol denat","risk_level": "High", "oily_risk": "Moderate","sensitive_risk": "High","dry_risk": "High", "combination_risk": "Moderate","normal_risk": "Moderate"},
        {"ingredient": "glycerin",     "risk_level": "Low",  "oily_risk": "Low",   "sensitive_risk": "Low",  "dry_risk": "Low",  "combination_risk": "Low",  "normal_risk": "Low"},
    ]

@pytest.fixture
def one_moderate_risk():
    return [
        {"ingredient": "glycerin",    "risk_level": "Low",      "oily_risk": "Low",  "sensitive_risk": "Low",      "dry_risk": "Low",      "combination_risk": "Low",  "normal_risk": "Low"},
        {"ingredient": "retinol",     "risk_level": "Moderate", "oily_risk": "Moderate","sensitive_risk": "High","dry_risk": "High",  "combination_risk": "Moderate","normal_risk": "Moderate"},
    ]


# Tests


class TestAnalyzeRisk:

    def test_all_low_returns_low(self, all_low_risk):
        result = analyze_risk(all_low_risk, skin_type="oily")
        assert result["overall_risk"] == "Low"

    def test_return_keys_present(self, all_low_risk):
        result = analyze_risk(all_low_risk, skin_type="oily")
        assert "low_risk" in result
        assert "moderate_risk" in result
        assert "high_risk" in result
        assert "overall_risk" in result

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="must not be empty"):
            analyze_risk([], skin_type="oily")

    # ── New threshold logic (post-fix) ────────────────────────────────────────

    def test_single_high_risk_ingredient_returns_moderate(self, one_high_risk):
        """Salicylic acid on dry skin = 1 high-risk → Moderate, not High."""
        result = analyze_risk(one_high_risk, skin_type="dry")
        assert result["overall_risk"] == "Moderate"

    def test_two_high_risk_returns_high(self, two_high_risk):
        """Fragrance + Alcohol Denat on sensitive = 2 high-risk → High."""
        result = analyze_risk(two_high_risk, skin_type="sensitive")
        assert result["overall_risk"] == "High"

    def test_one_moderate_returns_moderate(self, one_moderate_risk):
        result = analyze_risk(one_moderate_risk, skin_type="normal")
        assert result["overall_risk"] == "Moderate"

    def test_skin_type_specific_column_used(self, one_high_risk):
        """Same formula — oily skin should see Low (salicylic acid oily_risk=Low)."""
        result = analyze_risk(one_high_risk, skin_type="oily")
        assert result["overall_risk"] == "Low"

    def test_counts_are_accurate(self, two_high_risk):
        result = analyze_risk(two_high_risk, skin_type="sensitive")
        assert result["high_risk"] == 2
        assert result["low_risk"] == 1

    def test_default_skin_type_normal(self, all_low_risk):
        result = analyze_risk(all_low_risk)
        assert result["overall_risk"] == "Low"

    def test_single_ingredient_low_risk(self):
        ingredients = [{"ingredient": "glycerin", "risk_level": "Low", "oily_risk": "Low",
                        "sensitive_risk": "Low", "dry_risk": "Low",
                        "combination_risk": "Low", "normal_risk": "Low"}]
        result = analyze_risk(ingredients, skin_type="oily")
        assert result["overall_risk"] == "Low"
        assert result["high_risk"] == 0
        assert result["moderate_risk"] == 0