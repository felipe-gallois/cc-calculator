from cc_calc.as_path_estimation import ASPath
from cc_calc.autonomous_system import AS
from cc_calc.country import Alpha2Code
from cc_calc.country_path_estimation import (
    ASCountryMap,
    CountryPath,
    estimate_path,
)


def test_when_as_path_is_empty_returns_empty_country_path() -> None:
    as_path = ASPath([])
    map = ASCountryMap({})

    country_path = estimate_path(as_path, map)

    assert country_path == CountryPath([])


def test_when_as_is_in_map_returns_path_with_country() -> None:
    as_path = ASPath([AS(65536)])
    map = ASCountryMap({AS(65536): Alpha2Code("US")})

    country_path = estimate_path(as_path, map)

    assert country_path == CountryPath([Alpha2Code("US")])


def test_when_as_is_not_in_map_ignores_as_in_path() -> None:
    as_path = ASPath([AS(65536)])
    map = ASCountryMap({})

    country_path = estimate_path(as_path, map)

    assert country_path == CountryPath([])
