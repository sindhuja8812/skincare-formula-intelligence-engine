
import pytest
from utils.parser import normalize_ingredient_name, parse_ingredients


# normalize_ingredient_name

class TestNormalizeIngredientName:

    def test_lowercase_passthrough(self):
        assert normalize_ingredient_name("glycerin") == "glycerin"

    def test_strips_whitespace(self):
        assert normalize_ingredient_name("  niacinamide  ") == "niacinamide"

    def test_collapses_internal_spaces(self):
        assert normalize_ingredient_name("green  tea  extract") == "green tea extract"

    def test_synonym_aqua(self):
        assert normalize_ingredient_name("Aqua") == "water"

    def test_synonym_vitamin_c(self):
        assert normalize_ingredient_name("Vitamin C") == "vitamin c (l-ascorbic acid)"

    def test_synonym_ascorbic_acid(self):
        assert normalize_ingredient_name("ascorbic acid") == "vitamin c (l-ascorbic acid)"

    def test_synonym_bha(self):
        assert normalize_ingredient_name("BHA") == "salicylic acid"

    def test_synonym_retinaldehyde(self):
        assert normalize_ingredient_name("Retinaldehyde") == "retinal"

    def test_synonym_cica(self):
        assert normalize_ingredient_name("cica") == "centella asiatica extract"

    def test_synonym_vitamin_b5(self):
        assert normalize_ingredient_name("Vitamin B5") == "panthenol"

    def test_synonym_parfum(self):
        assert normalize_ingredient_name("Parfum") == "fragrance"

    def test_synonym_zinc(self):
        assert normalize_ingredient_name("zinc") == "zinc pca"

    def test_unknown_ingredient_returned_as_is(self):
        assert normalize_ingredient_name("unknowningredient123") == "unknowningredient123"

    def test_empty_string(self):
        assert normalize_ingredient_name("") == ""

    def test_uppercase_converted(self):
        assert normalize_ingredient_name("NIACINAMIDE") == "niacinamide"


# parse_ingredients

class TestParseIngredients:

    def test_newline_split(self):
        result = parse_ingredients("Niacinamide\nGlycerin\nSqualane")
        assert result == ["niacinamide", "glycerin", "squalane"]

    def test_comma_split(self):
        result = parse_ingredients("Niacinamide, Glycerin, Squalane")
        assert result == ["niacinamide", "glycerin", "squalane"]

    def test_semicolon_split(self):
        result = parse_ingredients("Niacinamide; Glycerin; Squalane")
        assert result == ["niacinamide", "glycerin", "squalane"]

    def test_deduplication(self):
        result = parse_ingredients("Niacinamide\nNiacinamide\nGlycerin")
        assert result.count("niacinamide") == 1

    def test_synonym_resolved_in_parse(self):
        result = parse_ingredients("Aqua\nBHA")
        assert "water" in result
        assert "salicylic acid" in result

    def test_empty_input(self):
        result = parse_ingredients("")
        assert result == []

    def test_mixed_separators(self):
        result = parse_ingredients("Niacinamide, Glycerin\nSqualane; Panthenol")
        assert len(result) == 4

    def test_whitespace_only_tokens_excluded(self):
        result = parse_ingredients("Niacinamide\n\n\nGlycerin")
        assert "" not in result

    def test_order_preserved(self):
        result = parse_ingredients("Squalane\nGlycerin\nNiacinamide")
        assert result == ["squalane", "glycerin", "niacinamide"]