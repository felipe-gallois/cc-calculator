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


def test_when_table_is_created_global_centrality_is_zero(
    counter: CentralityTable,
) -> None:
    assert counter.get_global() == 0


@pytest.mark.parametrize("points", [1, 2])
def test_when_updated_once_global_centrality_is_returned(
    points: int,
    counter: CentralityTable,
) -> None:
    counter.add_global(points)
    assert counter.get_global() == points


def test_when_updated_twice_total_global_centrality_is_returned(
    counter: CentralityTable,
) -> None:
    counter.add_global(1)
    counter.add_global(1)
    assert counter.get_global() == 2


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


def test_when_country_centrality_is_updated_global_centrality_stays_the_same(
    counter: CentralityTable,
) -> None:
    counter.add(Alpha2Code("BR"), 1)
    assert counter.get_global() == 0


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
    counter.add_global(1)
    assert counter.get_normalized(dummy_country) == pytest.approx(1.0)


def test_when_updated_one_centrality_is_zero_for_other_countries(
    counter: CentralityTable,
    dummy_country: Alpha2Code,
) -> None:
    counter.add(Alpha2Code("CA"), 1)
    counter.add_global(1)
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

    assert new_counter.get_normalized(Alpha2Code("CA")) == pytest.approx(1)


@pytest.mark.parametrize("excused,normalized", [(2, 1), (1, 0.5)])
def test_when_points_are_excused_for_country_it_changes_normalized_centrality(
    excused: int,
    normalized: int,
    counter: CentralityTable,
) -> None:
    counter.add(Alpha2Code("US"), 1)
    counter.add_global(3)
    counter.add_excused(Alpha2Code("US"), excused)
    assert counter.get_normalized(Alpha2Code("US")) == pytest.approx(normalized)


def test_when_points_are_excused_twice_for_country_it_changes_normalized_centrality(
    counter: CentralityTable,
) -> None:
    counter.add(Alpha2Code("US"), 1)
    counter.add_global(3)
    counter.add_excused(Alpha2Code("US"), 1)
    counter.add_excused(Alpha2Code("US"), 1)
    assert counter.get_normalized(Alpha2Code("US")) == pytest.approx(1)


@pytest.mark.parametrize(
    "country,excused",
    [(Alpha2Code("BR"), Alpha2Code("US")), (Alpha2Code("CA"), Alpha2Code("MX"))],
)
def test_when_points_are_excused_for_country_it_does_not_change_other_country(
    country: Alpha2Code,
    excused: Alpha2Code,
    counter: CentralityTable,
) -> None:
    counter.add(country, 1)
    counter.add_global(3)
    counter.add_excused(excused, 1)
    assert counter.get_normalized(country) == pytest.approx(1 / 3)


@pytest.mark.parametrize("excused", [1, 2])
def test_when_added_excused_it_returns_excused(
    excused: int,
    counter: CentralityTable,
) -> None:
    counter.add_excused(Alpha2Code("BR"), excused)
    assert counter.get_excused(Alpha2Code("BR")) == excused


@pytest.mark.parametrize("excused", [1, 2])
def test_when_combined_it_sums_excused(
    excused: int,
    counter: CentralityTable,
) -> None:
    counter.add_excused(Alpha2Code("BR"), excused)
    new_counter = CentralityTable()
    combined = new_counter.combine(counter)
    assert combined.get_excused(Alpha2Code("BR")) == excused


def test_when_country_centrality_increases_combined_global_centrality_is_zero(
    counter: CentralityTable,
) -> None:
    new_counter = CentralityTable()
    counter.add(Alpha2Code("BR"), 1)
    assert new_counter.combine(counter).get_global() == 0
