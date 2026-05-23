import pytest

from cc_calc.core._country_code import Alpha2Code, Alpha2FormatError


class TestCreateAlpha2Code:
    def test_when_country_code_in_correct_format_does_not_raise_exception(self) -> None:
        Alpha2Code("US")

    def test_country_code_with_less_than_one_character_raises_exception(self) -> None:
        with pytest.raises(Alpha2FormatError):
            Alpha2Code("U")

    def test_country_code_with_more_than_one_character_raises_exception(self) -> None:
        with pytest.raises(Alpha2FormatError):
            Alpha2Code("USA")

    def test_country_with_non_alpha_characters_raises_exception(self) -> None:
        with pytest.raises(Alpha2FormatError):
            Alpha2Code("U5")


class TestCompareAlpha2Code:
    def test_equality_with_another_type_returns_false(self) -> None:
        country_a = "US"
        country_b = Alpha2Code("US")

        assert country_a != country_b

    def test_countries_with_same_code_are_equal(self) -> None:
        country_a = Alpha2Code("US")
        country_b = Alpha2Code("US")

        assert country_a == country_b

    def test_countries_with_different_codes_are_not_equal(self) -> None:
        country_a = Alpha2Code("US")
        country_b = Alpha2Code("CA")

        assert country_a != country_b

    def test_countries_with_different_cases_are_equal(self) -> None:
        country_a = Alpha2Code("us")
        country_b = Alpha2Code("US")

        assert country_a == country_b
