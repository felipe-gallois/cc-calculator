import math

from cc_calc.centrality_metric import update_centrality
from cc_calc.country import Alpha2Code
from cc_calc.country_path_estimation import CountryPath


def test_when_path_has_no_countries_centrality_is_not_updated() -> None:
    path = CountryPath([])
    prefix_weights = (256, 256)

    centrality = update_centrality(path, prefix_weights)

    assert centrality.get(Alpha2Code("US")) == 0


def test_when_path_has_three_countries_centrality_of_intermediate_is_updated() -> None:
    path = CountryPath([Alpha2Code("CA"), Alpha2Code("US"), Alpha2Code("BR")])
    prefix_weights = (256, 256)

    centrality = update_centrality(path, prefix_weights)

    assert centrality.get(Alpha2Code("US")) == math.prod(prefix_weights)


def test_when_path_has_repeated_country_centrality_is_updated_once() -> None:
    path = CountryPath(
        [
            Alpha2Code("CA"),
            Alpha2Code("US"),
            Alpha2Code("MX"),
            Alpha2Code("US"),
            Alpha2Code("BR"),
        ]
    )
    prefix_weights = (256, 256)

    centrality = update_centrality(path, prefix_weights)

    assert centrality.get(Alpha2Code("US")) == math.prod(prefix_weights)


def test_when_path_has_three_countries_centrality_of_origin_is_not_updated() -> None:
    path = CountryPath([Alpha2Code("CA"), Alpha2Code("US"), Alpha2Code("BR")])
    prefix_weights = (256, 256)

    centrality = update_centrality(path, prefix_weights)

    assert centrality.get(Alpha2Code("CA")) == 0


def test_when_path_has_three_countries_centrality_of_dest_is_not_updated() -> None:
    path = CountryPath([Alpha2Code("CA"), Alpha2Code("US"), Alpha2Code("BR")])
    prefix_weights = (256, 256)

    centrality = update_centrality(path, prefix_weights)

    assert centrality.get(Alpha2Code("BR")) == 0


def test_when_centrality_was_not_zero_update_increments_centrality() -> None:
    path = CountryPath([Alpha2Code("CA"), Alpha2Code("US"), Alpha2Code("BR")])
    prefix_weights = (256, 256)

    centrality = update_centrality(path, prefix_weights)
    new_centrality = update_centrality(path, prefix_weights, centralities=centrality)

    assert new_centrality.get(Alpha2Code("US")) == 2 * math.prod(prefix_weights)
