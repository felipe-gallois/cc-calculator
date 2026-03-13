import math

import pytest

from cc_calc.centrality_table import CentralityTable


def test_country_centrality_starts_at_zero() -> None:
    counter = CentralityTable()
    assert counter.get("US") == 0


def test_when_added_country_centrality_is_retained() -> None:
    counter = CentralityTable()
    counter.add("US", 1)
    assert counter.get("US") == 1


def test_when_not_updated_normalized_centrality_returns_nan() -> None:
    counter = CentralityTable()
    assert math.isnan(counter.get_normalized("US"))


def test_when_updated_once_centrality_returns_one_for_country() -> None:
    counter = CentralityTable()
    counter.add("US", 1)
    assert counter.get_normalized("US") == pytest.approx(1.0)


def test_when_updated_one_centrality_is_zero_for_other_countries() -> None:
    counter = CentralityTable()
    counter.add("CA", 1)
    assert counter.get_normalized("US") == pytest.approx(0.0)
