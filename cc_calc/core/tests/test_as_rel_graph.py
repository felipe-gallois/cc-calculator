import pytest

from cc_calc.core._as_path import ASPath
from cc_calc.core._as_rel_graph import (
    ASRel,
    ASRelGraph,
    MissingASError,
    RelType,
)
from cc_calc.core._autonomous_system_number import ASN


class TestGetASPath:
    def test_when_src_and_dst_ases_are_the_same_path_contains_only_as(self) -> None:
        graph = ASRelGraph()
        graph.add_rel(ASRel(ASN(65536), ASN(65537), RelType.PROVIDER))

        assert graph.get_as_path(ASN(65536), ASN(65536)) == ASPath([ASN(65536)])

    def test_when_src_and_dst_are_one_hop_appart_returns_path_with_both_ases(
        self,
    ) -> None:
        graph = ASRelGraph()
        graph.add_rel(ASRel(ASN(65536), ASN(65537), RelType.PROVIDER))

        assert graph.get_as_path(ASN(65536), ASN(65537)) == ASPath(
            [ASN(65536), ASN(65537)]
        )

    def test_when_src_and_dst_are_two_hops_appart_returns_path_with_three_ases(
        self,
    ) -> None:
        graph = ASRelGraph()
        graph.add_rel(ASRel(ASN(65536), ASN(65537), RelType.PROVIDER))
        graph.add_rel(ASRel(ASN(65537), ASN(65538), RelType.PROVIDER))

        assert graph.get_as_path(ASN(65536), ASN(65538)) == ASPath(
            [ASN(65536), ASN(65537), ASN(65538)]
        )

    def test_when_as_not_in_path_it_is_not_included_in_result(self) -> None:
        graph = ASRelGraph()
        graph.add_rel(ASRel(ASN(65536), ASN(65537), RelType.PROVIDER))
        graph.add_rel(ASRel(ASN(65537), ASN(65538), RelType.PROVIDER))
        graph.add_rel(ASRel(ASN(65537), ASN(65539), RelType.PROVIDER))

        assert graph.get_as_path(ASN(65536), ASN(65538)) == ASPath(
            [ASN(65536), ASN(65537), ASN(65538)]
        )

    def test_when_src_or_dst_is_not_in_graph_raises_exception(self) -> None:
        graph = ASRelGraph()
        graph.add_rel(ASRel(ASN(65537), ASN(65538), RelType.PROVIDER))

        with pytest.raises(MissingASError):
            graph.get_as_path(ASN(65536), ASN(65537))

        with pytest.raises(MissingASError):
            graph.get_as_path(ASN(65538), ASN(65539))

    def test_when_path_does_not_exist_raises_exception(self) -> None:
        graph = ASRelGraph()
        graph.add_rel(ASRel(ASN(65536), ASN(65537), RelType.PROVIDER))
        graph.add_rel(ASRel(ASN(65538), ASN(65539), RelType.PROVIDER))

        with pytest.raises(MissingASError):
            graph.get_as_path(ASN(65536), ASN(65539))

    def test_when_path_has_peer_relationship_returns_path(self) -> None:
        graph = ASRelGraph()
        graph.add_rel(ASRel(ASN(65537), ASN(65536), RelType.PEER))

        assert graph.get_as_path(ASN(65536), ASN(65537)) == ASPath(
            [ASN(65536), ASN(65537)]
        )

    def test_when_only_path_goes_down_then_up_raises_exception(self) -> None:
        graph = ASRelGraph()
        graph.add_rel(ASRel(ASN(65536), ASN(65537), RelType.PROVIDER))
        graph.add_rel(ASRel(ASN(65538), ASN(65537), RelType.PROVIDER))

        with pytest.raises(MissingASError):
            graph.get_as_path(ASN(65536), ASN(65538))

    def test_when_only_path_goes_sideways_twice_raises_exception(self) -> None:
        graph = ASRelGraph()
        graph.add_rel(ASRel(ASN(65538), ASN(65537), RelType.PEER))
        graph.add_rel(ASRel(ASN(65537), ASN(65536), RelType.PEER))

        with pytest.raises(MissingASError):
            graph.get_as_path(ASN(65536), ASN(65538))


class TestCloneASRelGraph:
    def test_when_trivial_graph_is_cloned_clone_is_trivial(self) -> None:
        graph = ASRelGraph()
        clone = graph.clone()
        assert clone.nodes == set()

    def test_when_cloned_graph_has_rel_clone_has_rel_too(self) -> None:
        graph = ASRelGraph()
        graph.add_rel(ASRel(ASN(65536), ASN(65537), RelType.PROVIDER))

        clone = graph.clone()

        assert clone.edges == {
            ASRel(ASN(65536), ASN(65537), RelType.PROVIDER),
            ASRel(ASN(65537), ASN(65536), RelType.CLIENT),
        }
