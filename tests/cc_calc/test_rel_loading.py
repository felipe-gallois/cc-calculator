from io import StringIO

import pytest

from cc_calc.rel_loading import CaidaRelLoader


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
        self, input: str, rels: set[tuple[str, str, str]]
    ) -> None:
        src = StringIO(input)

        graph = CaidaRelLoader._build_graph(src)

        assert set(graph.edges(data="type")) == rels
