import pytest

from cc_calc.core._as_path import ASPath
from cc_calc.core._as_rel_graph import (
    ASRel,
    ASRelGraph,
    ASRelGraphError,
    RelType,
)
from cc_calc.core._autonomous_system_number import ASN


class TestGetASPath:
    def test_when_src_and_dst_ases_are_the_same_path_contains_only_as(self) -> None:
        graph = ASRelGraph()
        graph.add_rel(ASRel(ASN(65536), ASN(65537), RelType.P2C))

        assert graph.get_as_path(ASN(65536), ASN(65536)) == ASPath([ASN(65536)])

    def test_when_src_and_dst_are_one_hop_appart_returns_path_with_both_ases(
        self,
    ) -> None:
        graph = ASRelGraph()
        graph.add_rel(ASRel(ASN(65536), ASN(65537), RelType.P2C))

        assert graph.get_as_path(ASN(65536), ASN(65537)) == ASPath(
            [ASN(65536), ASN(65537)]
        )

    def test_when_src_and_dst_are_two_hops_appart_returns_path_with_three_ases(
        self,
    ) -> None:
        graph = ASRelGraph()
        graph.add_rel(ASRel(ASN(65536), ASN(65537), RelType.P2C))
        graph.add_rel(ASRel(ASN(65537), ASN(65538), RelType.P2C))

        assert graph.get_as_path(ASN(65536), ASN(65538)) == ASPath(
            [ASN(65536), ASN(65537), ASN(65538)]
        )

    def test_when_as_not_in_path_it_is_not_included_in_result(self) -> None:
        graph = ASRelGraph()
        graph.add_rel(ASRel(ASN(65536), ASN(65537), RelType.P2C))
        graph.add_rel(ASRel(ASN(65537), ASN(65538), RelType.P2C))
        graph.add_rel(ASRel(ASN(65537), ASN(65539), RelType.P2C))

        assert graph.get_as_path(ASN(65536), ASN(65538)) == ASPath(
            [ASN(65536), ASN(65537), ASN(65538)]
        )

    def test_when_src_or_dst_is_not_in_graph_raises_exception(self) -> None:
        graph = ASRelGraph()
        graph.add_rel(ASRel(ASN(65537), ASN(65538), RelType.P2C))

        with pytest.raises(ASRelGraphError):
            graph.get_as_path(ASN(65536), ASN(65537))

        with pytest.raises(ASRelGraphError):
            graph.get_as_path(ASN(65538), ASN(65539))

    def test_when_path_does_not_exist_raises_exception(self) -> None:
        graph = ASRelGraph()
        graph.add_rel(ASRel(ASN(65536), ASN(65537), RelType.P2C))
        graph.add_rel(ASRel(ASN(65538), ASN(65539), RelType.P2C))

        with pytest.raises(ASRelGraphError):
            graph.get_as_path(ASN(65536), ASN(65539))

    def test_when_path_has_peer_relationship_returns_path(self) -> None:
        graph = ASRelGraph()
        graph.add_rel(ASRel(ASN(65537), ASN(65536), RelType.P2P))

        assert graph.get_as_path(ASN(65536), ASN(65537)) == ASPath(
            [ASN(65536), ASN(65537)]
        )

    def test_when_only_path_goes_down_then_up_raises_exception(self) -> None:
        graph = ASRelGraph()
        graph.add_rel(ASRel(ASN(65536), ASN(65537), RelType.P2C))
        graph.add_rel(ASRel(ASN(65538), ASN(65537), RelType.P2C))

        with pytest.raises(ASRelGraphError):
            graph.get_as_path(ASN(65536), ASN(65538))

    def test_when_only_path_goes_sideways_twice_raises_exception(self) -> None:
        graph = ASRelGraph()
        graph.add_rel(ASRel(ASN(65538), ASN(65537), RelType.P2P))
        graph.add_rel(ASRel(ASN(65537), ASN(65536), RelType.P2P))

        with pytest.raises(ASRelGraphError):
            graph.get_as_path(ASN(65536), ASN(65538))
