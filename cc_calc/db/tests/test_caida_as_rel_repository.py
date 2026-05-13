from io import StringIO

import pytest

from cc_calc.core import ASN, ASRel, RelType
from cc_calc.db._caida_as_rel_repository import _build_graph


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
                {ASN(12), ASN(12345)},
            ),
            (
                "12|12345|0|bgp\n12|45678|0|bgp\n",
                {ASN(12), ASN(12345), ASN(45678)},
            ),
        ],
    )
    def test_loads_ases_from_announcements(self, input: str, peers: set[ASN]) -> None:
        src = StringIO(input)
        graph = _build_graph(src)
        assert graph.nodes == peers

    @pytest.mark.parametrize(
        "input, rels",
        [
            (
                "12|12345|-1|bgp",
                {
                    ASRel(ASN(12), ASN(12345), RelType.P2C),
                },
            ),
            (
                "12|12345|0|bgp",
                {ASRel(ASN(12), ASN(12345), RelType.P2P)},
            ),
        ],
    )
    def test_loads_rels_from_announcements(self, input: str, rels: set[ASRel]) -> None:
        src = StringIO(input)
        graph = _build_graph(src)
        assert graph.edges == rels
