import pytest

from cc_calc.as_path_estimation import ASRel, ASRelGraph, ASRelGraphError, RelType
from cc_calc.autonomous_system import AS


class TestListPathReceivers:
    def test_if_as_not_in_graph_raise_error(self) -> None:
        graph = ASRelGraph()

        with pytest.raises(ASRelGraphError):
            graph.bgp_receivers_from_as("1")

    @pytest.mark.parametrize(
        "topology, receivers",
        [
            ({ASRel(AS(1), AS(2), RelType.P2P)}, {AS(2)}),
            (
                {
                    ASRel(AS(1), AS(2), RelType.P2P),
                    ASRel(AS(1), AS(3), RelType.P2P),
                },
                {AS(2), AS(3)},
            ),
        ],
    )
    def test_when_originates_new_path_propagate_to_all(
        self, topology: set[ASRel], receivers: set[AS]
    ) -> None:
        graph = ASRelGraph()

        for rel in topology:
            graph.add_rel(rel)

        assert graph.bgp_receivers_from_as("1") == receivers

    @pytest.mark.parametrize(
        "topology, receivers",
        [
            (
                {
                    ASRel(AS(1), AS(2), RelType.P2P),
                    ASRel(AS(2), AS(3), RelType.P2P),
                },
                set(),
            ),
            (
                {
                    ASRel(AS(1), AS(2), RelType.P2P),
                    ASRel(AS(2), AS(3), RelType.P2C),
                },
                {AS(3)},
            ),
            (
                {
                    ASRel(AS(1), AS(2), RelType.P2P),
                    ASRel(AS(3), AS(2), RelType.P2C),
                },
                set(),
            ),
            (
                {
                    ASRel(AS(2), AS(1), RelType.P2C),
                    ASRel(AS(2), AS(3), RelType.P2P),
                },
                {AS(3)},
            ),
        ],
    )
    def test_when_receives_prefix_from_third_party_propagate_according_to_valley_free(
        self, topology: set[ASRel], receivers: set[AS]
    ) -> None:
        graph = ASRelGraph()

        for rel in topology:
            graph.add_rel(rel)

        assert graph.bgp_receivers_from_as("2", prev_as="1") == receivers
