import pytest

from cc_calc.country import Country, CountryError


class TestCreateCountry:
    def test_country_code_with_less_than_one_character_raises_exception(self) -> None:
        with pytest.raises(CountryError):
            Country("U")

    def test_country_code_with_more_than_one_character_raises_exception(self) -> None:
        with pytest.raises(CountryError):
            Country("USA")

    def test_country_with_non_alpha_characters_raises_exception(self) -> None:
        with pytest.raises(CountryError):
            Country("U5")


class TestCompareCountry:
    def test_equality_with_another_type_returns_false(self) -> None:
        country_a = "US"
        country_b = Country("US")

        assert country_a != country_b

    def test_countries_with_same_code_are_equal(self) -> None:
        country_a = Country("US")
        country_b = Country("US")

        assert country_a == country_b

    def test_countries_with_different_codes_are_not_equal(self) -> None:
        country_a = Country("US")
        country_b = Country("CA")

        assert country_a != country_b

    def test_countries_with_different_cases_are_equal(self) -> None:
        country_a = Country("us")
        country_b = Country("US")

        assert country_a == country_b
