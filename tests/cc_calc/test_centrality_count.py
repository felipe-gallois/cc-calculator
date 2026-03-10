import math

import pytest

from cc_calc.centrality_count import CentralityCounter


def test_country_centrality_starts_at_zero() -> None:
    counter = CentralityCounter()
    assert counter.get("US") == 0


def test_when_added_country_centrality_is_retained() -> None:
    counter = CentralityCounter()
    counter.add("US", 1)
    assert counter.get("US") == 1


def test_when_not_updated_normalized_centrality_returns_nan() -> None:
    counter = CentralityCounter()
    assert math.isnan(counter.get_normalized("US"))


def test_when_updated_once_centrality_returns_one_for_country() -> None:
    counter = CentralityCounter()
    counter.add("US", 1)
    assert counter.get_normalized("US") == pytest.approx(1.0)


def test_when_updated_one_centrality_is_zero_for_other_countries() -> None:
    counter = CentralityCounter()
    counter.add("CA", 1)
    assert counter.get_normalized("US") == pytest.approx(0.0)
