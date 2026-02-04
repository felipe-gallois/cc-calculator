from io import StringIO

import networkx as nx
import pytest

from cc_calc.bgp_simulation import AS
from cc_calc.rel_loading import CaidaRelLoader, NetworkXRelGraph


class TestListPathReceivers:
    @pytest.mark.parametrize(
        "topology, receivers",
        [
            ([("1", "2", {"type": "peer"})], {"2"}),
            ([("1", "2", {"type": "peer"}), ("1", "3", {"type": "peer"})], {"2", "3"}),
        ],
    )
    def test_when_originates_new_path_propagate_to_all(
        self, topology: list[tuple[AS, AS, dict[str, str]]], receivers: set[AS]
    ) -> None:
        graph = NetworkXRelGraph(nx.DiGraph(topology))

        assert graph.bgp_receivers_from_as("1") == receivers

    @pytest.mark.parametrize(
        "topology, receivers",
        [
            ([("1", "2", {"type": "peer"}), ("2", "3", {"type": "peer"})], set()),
            ([("1", "2", {"type": "peer"}), ("2", "3", {"type": "customer"})], {"3"}),
            ([("1", "2", {"type": "customer"}), ("2", "3", {"type": "peer"})], {"3"}),
        ],
    )
    def test_when_receives_prefix_from_third_party_propagate_according_to_valley_free(
        self, topology: list[tuple[AS, AS, dict[str, str]]], receivers: set[AS]
    ) -> None:
        graph = NetworkXRelGraph(nx.DiGraph(topology))

        assert graph.bgp_receivers_from_as("2", prev_as="1") == receivers


class TestLoadCaidaRels:
    @pytest.mark.parametrize("input", ["", "\n", "# commented"])
    def test_loads_no_ases_for_empty_input(self, input: str) -> None:
        src = StringIO(input)

        graph = CaidaRelLoader._build_graph(src)

        assert not graph.nodes

    @pytest.mark.parametrize(
        "input, peers",
        [
            (
                "12|12345|0|bgp",
                {"12", "12345"},
            ),
            (
                "12|12345|0|bgp\n12|45678|0|bgp\n",
                {"12", "12345", "45678"},
            ),
        ],
    )
    def test_loads_ases_from_announcements(self, input: str, peers: set[AS]) -> None:
        src = StringIO(input)

        graph = CaidaRelLoader._build_graph(src)

        assert set(graph.nodes) == peers

    @pytest.mark.parametrize(
        "input, rels",
        [
            (
                "12|12345|-1|bgp",
                {("12", "12345", "provider"), ("12345", "12", "custumer")},
            ),
            (
                "12|12345|0|bgp",
                {("12", "12345", "peer"), ("12345", "12", "peer")},
            ),
        ],
    )
    def test_loads_rels_from_announcements(
        self, input: str, rels: set[tuple[AS, AS, str]]
    ) -> None:
        src = StringIO(input)

        graph = CaidaRelLoader._build_graph(src)

        assert set(graph.edges(data="type")) == rels
