import math

import pytest

from cc_calc.centrality_metric._centrality_table import CentralityTable
from cc_calc.country import Alpha2Code


@pytest.fixture
def dummy_country() -> Alpha2Code:
    return Alpha2Code("US")


def test_country_centrality_starts_at_zero(dummy_country: Alpha2Code) -> None:
    counter = CentralityTable()
    assert counter.get(dummy_country) == 0


def test_when_added_country_centrality_is_retained(dummy_country: Alpha2Code) -> None:
    counter = CentralityTable()
    counter.add(dummy_country, 1)
    assert counter.get(dummy_country) == 1


def test_when_not_updated_normalized_centrality_returns_nan(
    dummy_country: Alpha2Code,
) -> None:
    counter = CentralityTable()
    assert math.isnan(counter.get_normalized(dummy_country))


def test_when_updated_once_centrality_returns_one_for_country(
    dummy_country: Alpha2Code,
) -> None:
    counter = CentralityTable()
    counter.add(dummy_country, 1)
    assert counter.get_normalized(dummy_country) == pytest.approx(1.0)


def test_when_updated_one_centrality_is_zero_for_other_countries(
    dummy_country: Alpha2Code,
) -> None:
    counter = CentralityTable()
    counter.add(Alpha2Code("CA"), 1)
    assert counter.get_normalized(dummy_country) == pytest.approx(0.0)
