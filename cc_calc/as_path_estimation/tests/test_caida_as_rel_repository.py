from io import StringIO

import pytest

from cc_calc.as_path_estimation import AS, ASRel, RelType
from cc_calc.as_path_estimation._caida_as_rel_repository import _build_graph


class TestLoadCaidaRels:
    @pytest.mark.parametrize("input", ["", "\n", "# commented"])
    def test_when_no_input_load_no_rels(self, input: str) -> None:
        src = StringIO(input)
        graph = _build_graph(src)
        assert not graph.nodes

    @pytest.mark.parametrize(
        "input, peers",
        [
            (
                "12|12345|0|bgp",
                {AS(12), AS(12345)},
            ),
            (
                "12|12345|0|bgp\n12|45678|0|bgp\n",
                {AS(12), AS(12345), AS(45678)},
            ),
        ],
    )
    def test_loads_ases_from_announcements(self, input: str, peers: set[AS]) -> None:
        src = StringIO(input)
        graph = _build_graph(src)
        assert graph.nodes == peers

    @pytest.mark.parametrize(
        "input, rels",
        [
            (
                "12|12345|-1|bgp",
                {
                    ASRel(AS(12), AS(12345), RelType.P2C),
                },
            ),
            (
                "12|12345|0|bgp",
                {ASRel(AS(12), AS(12345), RelType.P2P)},
            ),
        ],
    )
    def test_loads_rels_from_announcements(self, input: str, rels: set[ASRel]) -> None:
        src = StringIO(input)
        graph = _build_graph(src)
        assert graph.edges == rels
