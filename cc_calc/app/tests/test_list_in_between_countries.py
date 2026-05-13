from cc_calc.app._list_in_between_countries import (
    list_in_between_countries,
)
from cc_calc.core import Alpha2Code, CountryPath


def test_when_path_only_has_src_or_dst_countries_returns_empty_set() -> None:
    src_country = Alpha2Code("BR")
    dst_country = Alpha2Code("CA")

    country_path = CountryPath([src_country, dst_country])

    in_between_countries = list_in_between_countries(
        country_path, src_country, dst_country
    )

    assert in_between_countries == set()


def test_when_path_contains_countries_other_than_src_and_dst_returns_them() -> None:
    src_country = Alpha2Code("BR")
    dst_country = Alpha2Code("CA")

    country_path = CountryPath([src_country, Alpha2Code("US"), dst_country])

    in_between_countries = list_in_between_countries(
        country_path, src_country, dst_country
    )

    assert in_between_countries == {Alpha2Code("US")}
