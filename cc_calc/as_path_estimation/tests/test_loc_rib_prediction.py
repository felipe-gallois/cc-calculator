import pytest
from pytest_mock import MockerFixture

from cc_calc.as_path_estimation import (
    ASPath,
    ASRelGraph,
    LocRIBModelError,
    PrefixSureASPathList,
    predict_loc_rib_model,
)
from cc_calc.autonomous_system import AS
from cc_calc.ip_prefix import IPPrefix


class TestPredictLocRIBModel:
    @pytest.fixture
    def dummy_path_list_one(self) -> PrefixSureASPathList:
        return PrefixSureASPathList(
            IPPrefix("192.0.2.0/24"), {ASPath((AS(65537), AS(65538), AS(65539)))}
        )

    @pytest.fixture
    def dummy_path_list_two(self) -> PrefixSureASPathList:
        return PrefixSureASPathList(
            IPPrefix("192.0.2.0/24"),
            {
                ASPath((AS(65537), AS(65538), AS(65539))),
                ASPath((AS(65536), AS(65537), AS(65538), AS(65539))),
            },
        )

    def test_when_single_path_is_known_predicts_paths_for_every_as_in_it(
        self,
        dummy_path_list_one: PrefixSureASPathList,
        mocker: MockerFixture,
    ) -> None:
        as_rel_stub = mocker.create_autospec(ASRelGraph)
        as_rel_stub.bgp_receivers_from_as.return_value = set()

        model = predict_loc_rib_model(as_rel_stub, dummy_path_list_one)

        dummy_path = ASPath((AS(65537), AS(65538), AS(65539)))

        for i in range(len(dummy_path)):
            src_as = dummy_path[i]
            expected_path = dummy_path[i:]

            if src_as is not None:
                assert model.best_path(src_as) == expected_path

    def test_when_there_is_peer_path_is_propagated(
        self,
        dummy_path_list_one: PrefixSureASPathList,
        mocker: MockerFixture,
    ) -> None:
        peer_as = AS(65536)

        as_rel_stub = mocker.create_autospec(ASRelGraph)
        as_rel_stub.bgp_receivers_from_as.side_effect = lambda curr_as, prev_as: (
            {peer_as} if curr_as == AS(65537) else set()
        )

        model = predict_loc_rib_model(as_rel_stub, dummy_path_list_one)

        dummy_path = ASPath((AS(65537), AS(65538), AS(65539)))

        assert model.best_path(peer_as) == dummy_path

    def test_when_as_is_disconnected_path_is_not_propagated(
        self,
        dummy_path_list_one: PrefixSureASPathList,
        mocker: MockerFixture,
    ) -> None:
        as_rel_stub = mocker.create_autospec(ASRelGraph)
        as_rel_stub.bgp_receivers_from_as.return_value = set()

        model = predict_loc_rib_model(as_rel_stub, dummy_path_list_one)

        with pytest.raises(LocRIBModelError):
            model.best_path(AS(65536))

    def test_when_there_is_a_two_peer_chain_path_is_propagated_to_the_end(
        self,
        dummy_path_list_one: PrefixSureASPathList,
        mocker: MockerFixture,
    ) -> None:
        peer_as_one = AS(65540)
        peer_as_two = AS(65541)

        def effect(curr_as: AS, prev_as: AS) -> set[AS]:
            if curr_as == AS(65537):
                return {peer_as_one}
            elif curr_as == peer_as_one:
                return {peer_as_two}
            else:
                return set()

        as_rel_stub = mocker.create_autospec(ASRelGraph)
        as_rel_stub.bgp_receivers_from_as.side_effect = effect

        model = predict_loc_rib_model(as_rel_stub, dummy_path_list_one)

        dummy_path = ASPath((AS(65537), AS(65538), AS(65539)))

        assert model.best_path(peer_as_two) == dummy_path.append(peer_as_one)

    def test_after_short_and_long_path_announcements_estimator_predicts_shortest_one(
        self,
        dummy_path_list_two: PrefixSureASPathList,
        mocker: MockerFixture,
    ) -> None:
        peer_as = AS(65540)

        as_rel_stub = mocker.create_autospec(ASRelGraph)
        as_rel_stub.bgp_receivers_from_as.side_effect = lambda curr_as, prev_as: (
            {peer_as} if curr_as == AS(65537) else set()
        )

        model = predict_loc_rib_model(as_rel_stub, dummy_path_list_two)

        dummy_path = ASPath((AS(65537), AS(65538), AS(65539)))

        assert model.best_path(peer_as) == dummy_path
