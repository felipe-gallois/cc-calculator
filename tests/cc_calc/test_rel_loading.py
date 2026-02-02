from io import StringIO

import pytest

from cc_calc.rel_loading import CaidaRelLoader

SINGLE_REGULAR_P2P_INPUT = "12|12345|0|bgp"

SINGLE_REGULAR_P2C_INPUT = "12|12345|-1|bgp"

MULTIPLE_REGULAR_P2P_INPUT = "12|12345|0|bgp\n12|45678|0|bgp\n"

COMMENTED_INPUT = "# commented"

SINGLE_REGULAR_P2P_PEERS = {"12", "12345"}

MULTIPLE_REGULAR_P2P_PEERS = {"12", "12345", "45678"}

SINGLE_REGULAR_P2C_RELS = {("12", "12345", "provider"), ("12345", "12", "custumer")}

SINGLE_REGULAR_P2P_RELS = {("12", "12345", "peer"), ("12345", "12", "peer")}


class TestLoadCaidaRels:
    @pytest.mark.parametrize("content", ["", "\n"])
    def test_loads_no_ases_for_empty_input(self, content: str) -> None:
        src = StringIO(content)

        relationships = CaidaRelLoader._build_graph(src)

        assert not relationships.nodes

    def test_loads_peers_in_announcement(self) -> None:
        src = StringIO(SINGLE_REGULAR_P2P_INPUT)

        relationships = CaidaRelLoader._build_graph(src)

        assert set(relationships.nodes) == SINGLE_REGULAR_P2P_PEERS

    def test_loads_peers_in_two_announcements(self) -> None:
        src = StringIO(MULTIPLE_REGULAR_P2P_INPUT)

        relationships = CaidaRelLoader._build_graph(src)

        assert set(relationships.nodes) == MULTIPLE_REGULAR_P2P_PEERS

    def test_loads_p2c_relationship(self) -> None:
        src = StringIO(SINGLE_REGULAR_P2C_INPUT)

        relationships = CaidaRelLoader._build_graph(src)

        assert set(relationships.edges(data="type")) == SINGLE_REGULAR_P2C_RELS

    def test_loads_p2p_relationships(self) -> None:
        src = StringIO(SINGLE_REGULAR_P2P_INPUT)

        relationships = CaidaRelLoader._build_graph(src)

        assert set(relationships.edges(data="type")) == SINGLE_REGULAR_P2P_RELS

    def test_when_line_is_commented_ignore(self) -> None:
        src = StringIO(COMMENTED_INPUT)

        relationships = CaidaRelLoader._build_graph(src)

        assert not relationships.nodes
