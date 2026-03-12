import networkx as nx
import pytest

from cc_calc.as_rel_graph import ASRelGraph, ASRelGraphError, _RelType
from cc_calc.autonomous_system import AS


def as_topo(
    str_topo: list[tuple[str, str, dict[str, str]]],
) -> list[tuple[AS, AS, dict[str, str]]]:
    return [(AS(x), AS(y), z) for x, y, z in str_topo]


def as_set(str_set: set[str]) -> set[AS]:
    return {AS(x) for x in str_set}


class TestListPathReceivers:
    def test_if_as_not_in_graph_raise_error(self) -> None:
        graph = ASRelGraph(nx.DiGraph())

        with pytest.raises(ASRelGraphError):
            graph.bgp_receivers_from_as("1")

    @pytest.mark.parametrize(
        "topology, receivers",
        [
            ([("1", "2", {"type": _RelType.PEER})], {"2"}),
            (
                [
                    ("1", "2", {"type": _RelType.PEER}),
                    ("1", "3", {"type": _RelType.PEER}),
                ],
                {"2", "3"},
            ),
        ],
    )
    def test_when_originates_new_path_propagate_to_all(
        self, topology: list[tuple[str, str, dict[str, str]]], receivers: set[str]
    ) -> None:
        graph = ASRelGraph(nx.DiGraph(as_topo(topology)))

        assert graph.bgp_receivers_from_as("1") == as_set(receivers)

    @pytest.mark.parametrize(
        "topology, receivers",
        [
            (
                [
                    ("1", "2", {"type": _RelType.PEER}),
                    ("2", "3", {"type": _RelType.PEER}),
                ],
                set(),
            ),
            (
                [
                    ("1", "2", {"type": _RelType.PEER}),
                    ("2", "3", {"type": _RelType.PROVIDER}),
                ],
                {"3"},
            ),
            (
                [
                    ("1", "2", {"type": _RelType.PEER}),
                    ("2", "3", {"type": _RelType.CUSTOMER}),
                ],
                set(),
            ),
            (
                [
                    ("1", "2", {"type": _RelType.CUSTOMER}),
                    ("2", "3", {"type": _RelType.PEER}),
                ],
                {"3"},
            ),
        ],
    )
    def test_when_receives_prefix_from_third_party_propagate_according_to_valley_free(
        self, topology: list[tuple[str, str, dict[str, str]]], receivers: set[str]
    ) -> None:
        graph = ASRelGraph(nx.DiGraph(as_topo(topology)))

        assert graph.bgp_receivers_from_as("2", prev_as="1") == as_set(receivers)
