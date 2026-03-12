from io import StringIO

import pytest

from cc_calc.autonomous_system import AS
from cc_calc.rel_loading import CaidaRelLoader, _RelType


def as_set(str_set: set[str]) -> set[AS]:
    return {AS(x) for x in str_set}


def as_edges(str_topo: set[tuple[str, str, str]]) -> set[tuple[AS, AS, str]]:
    return {(AS(x), AS(y), z) for x, y, z in str_topo}


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
    def test_loads_ases_from_announcements(self, input: str, peers: set[str]) -> None:
        src = StringIO(input)

        graph = CaidaRelLoader._build_graph(src)

        assert set(graph.nodes) == as_set(peers)

    @pytest.mark.parametrize(
        "input, rels",
        [
            (
                "12|12345|-1|bgp",
                {
                    ("12", "12345", _RelType.PROVIDER),
                    ("12345", "12", _RelType.CUSTOMER),
                },
            ),
            (
                "12|12345|0|bgp",
                {("12", "12345", _RelType.PEER), ("12345", "12", _RelType.PEER)},
            ),
        ],
    )
    def test_loads_rels_from_announcements(
        self, input: str, rels: set[tuple[str, str, str]]
    ) -> None:
        src = StringIO(input)

        graph = CaidaRelLoader._build_graph(src)

        assert set(graph.edges(data="type")) == as_edges(rels)
