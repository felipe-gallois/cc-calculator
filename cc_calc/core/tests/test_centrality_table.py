import math

import pytest

from cc_calc.core._centrality_table import CentralityTable
from cc_calc.core._country_code import Alpha2Code


@pytest.fixture
def counter() -> CentralityTable:
    return CentralityTable()


@pytest.fixture
def dummy_country() -> Alpha2Code:
    return Alpha2Code("US")


def test_when_no_points_were_added_view_returns_nothing(
    counter: CentralityTable,
) -> None:
    items = counter.items()
    assert len(items) == 0


def test_when_points_were_added_to_a_country_view_returns_them(
    counter: CentralityTable,
    dummy_country: Alpha2Code,
) -> None:
    counter.add(dummy_country, 1)

    items = counter.items()

    assert items == {dummy_country: 1}.items()


def test_when_centrality_points_is_zero_it_does_not_create_item(
    counter: CentralityTable,
    dummy_country: Alpha2Code,
) -> None:
    counter.add(dummy_country, 0)

    items = counter.items()

    assert len(items) == 0


def test_country_centrality_starts_at_zero(
    counter: CentralityTable, dummy_country: Alpha2Code
) -> None:
    assert counter.get(dummy_country) == 0


def test_when_added_country_centrality_is_retained(
    counter: CentralityTable, dummy_country: Alpha2Code
) -> None:
    counter.add(dummy_country, 1)
    assert counter.get(dummy_country) == 1


def test_when_table_is_created_using_constructor_centralities_take_effect() -> None:
    counter = CentralityTable({Alpha2Code("BR"): 50})
    assert counter.items() == {Alpha2Code("BR"): 50}.items()


def test_when_constructor_creates_table_normalized_centralities_are_correct() -> None:
    counter = CentralityTable({Alpha2Code("BR"): 50})
    assert counter.get_normalized(Alpha2Code("BR")) == 1


def test_when_not_updated_normalized_centrality_returns_nan(
    counter: CentralityTable,
    dummy_country: Alpha2Code,
) -> None:
    assert math.isnan(counter.get_normalized(dummy_country))


def test_when_updated_once_centrality_returns_one_for_country(
    counter: CentralityTable,
    dummy_country: Alpha2Code,
) -> None:
    counter.add(dummy_country, 1)
    assert counter.get_normalized(dummy_country) == pytest.approx(1.0)


def test_when_updated_one_centrality_is_zero_for_other_countries(
    counter: CentralityTable,
    dummy_country: Alpha2Code,
) -> None:
    counter.add(Alpha2Code("CA"), 1)
    assert counter.get_normalized(dummy_country) == pytest.approx(0.0)


def test_when_counter_is_combined_to_another_it_sums_the_points_of_each(
    counter: CentralityTable,
) -> None:
    counter.add(Alpha2Code("CA"), 2)

    other_counter = CentralityTable({Alpha2Code("CA"): 1})
    new_counter = other_counter.combine(counter)

    assert new_counter.items() == {Alpha2Code("CA"): 3}.items()


def test_when_counter_is_combined_to_another_normalized_centralities_stay_correct(
    counter: CentralityTable,
) -> None:
    counter.add(Alpha2Code("CA"), 2)

    new_counter = CentralityTable({Alpha2Code("CA"): 1})
    new_counter.combine(counter)

    assert new_counter.get_normalized(Alpha2Code("CA")) == 1
