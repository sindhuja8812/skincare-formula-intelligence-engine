
import pytest
from utils.benefits import extract_benefits, extract_concerns

# Fixtures

@pytest.fixture
def multi_benefit_ingredients():
    return [
        {"ingredient": "niacinamide",   "benefits": "Brightening|Oil Control|Barrier Repair", "concerns": "None"},
        {"ingredient": "zinc pca",      "benefits": "Oil Control|Acne Support",                "concerns": "None"},
        {"ingredient": "green tea",     "benefits": "Antioxidant|Anti-Inflammatory|Oil Control","concerns": "None"},
    ]

@pytest.fixture
def concern_ingredients():
    return [
        {"ingredient": "salicylic acid","benefits": "Exfoliation|Acne Support", "concerns": "Irritation Risk|Dryness Risk"},
        {"ingredient": "retinol",       "benefits": "Anti-Aging",               "concerns": "Irritation Risk|Dryness Risk|Photosensitivity"},
        {"ingredient": "glycerin",      "benefits": "Hydration",                "concerns": "None"},
    ]

@pytest.fixture
def none_benefits():
    return [
        {"ingredient": "xanthan gum", "benefits": "None", "concerns": "None"},
        {"ingredient": "carbomer",    "benefits": "None", "concerns": "None"},
    ]

# extract_benefits

class TestExtractBenefits:

    def test_returns_list(self, multi_benefit_ingredients):
        result = extract_benefits(multi_benefit_ingredients)
        assert isinstance(result, list)

    def test_most_common_first(self, multi_benefit_ingredients):
        result = extract_benefits(multi_benefit_ingredients)
        # Oil Control appears 3 times, should be first
        assert result[0] == "Oil Control"

    def test_none_values_excluded(self, none_benefits):
        result = extract_benefits(none_benefits)
        assert result == []

    def test_deduplication(self, multi_benefit_ingredients):
        result = extract_benefits(multi_benefit_ingredients)
        assert len(result) == len(set(result))

    def test_single_ingredient(self):
        ings = [{"ingredient": "glycerin", "benefits": "Hydration|Moisture Retention", "concerns": "None"}]
        result = extract_benefits(ings)
        assert "Hydration" in result
        assert "Moisture Retention" in result

    def test_missing_benefits_key(self):
        ings = [{"ingredient": "water"}]   # no benefits key
        result = extract_benefits(ings)
        assert result == []

# extract_concerns

class TestExtractConcerns:

    def test_returns_list(self, concern_ingredients):
        result = extract_concerns(concern_ingredients)
        assert isinstance(result, list)

    def test_repeated_concern_surfaces(self, concern_ingredients):
        # Irritation Risk appears in 2 of 3 ingredients → should be flagged
        result = extract_concerns(concern_ingredients)
        assert "Irritation Risk" in result

    def test_single_occurrence_suppressed_with_3_ingredients(self, concern_ingredients):
        # Photosensitivity appears only once out of 3 → suppressed
        result = extract_concerns(concern_ingredients)
        assert "Photosensitivity" not in result

    def test_none_values_excluded(self, none_benefits):
        result = extract_concerns(none_benefits)
        assert result == []

    def test_threshold_1_for_small_formula(self):
        # Only 2 ingredients — threshold drops to 1
        ings = [
            {"ingredient": "retinol",  "benefits": "Anti-Aging", "concerns": "Photosensitivity"},
            {"ingredient": "glycerin", "benefits": "Hydration",  "concerns": "None"},
        ]
        result = extract_concerns(ings)
        assert "Photosensitivity" in result


