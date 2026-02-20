import pytest
from pytest_mock import MockerFixture

from cc_calc.autonomous_system import AS, ASPath
from cc_calc.bgp_simulation import (
    ASPathEstimationError,
    ASRelGraph,
    SimpleASPathEstimator,
)


class TestEstimateASPath:
    @pytest.fixture
    def estimator(self) -> SimpleASPathEstimator:
        return SimpleASPathEstimator()

    @pytest.fixture
    def dummy_path(self) -> ASPath:
        return ASPath((AS(65537), AS(65538), AS(65539)))

    @pytest.fixture
    def dummy_path_two(self) -> ASPath:
        return ASPath((AS(65536), AS(65537), AS(65538), AS(65539)))

    def test_when_not_fitted_prediction_raises_exception(
        self, estimator: SimpleASPathEstimator
    ) -> None:
        with pytest.raises(ASPathEstimationError):
            estimator.predict(AS(65536))

    def test_when_single_path_is_known_predicts_paths_for_every_as_in_it(
        self,
        estimator: SimpleASPathEstimator,
        dummy_path: ASPath,
        mocker: MockerFixture,
    ) -> None:
        as_rel_stub = mocker.create_autospec(ASRelGraph)
        as_rel_stub.bgp_receivers_from_as.return_value = set()

        estimator.fit(as_rel_stub, {dummy_path})

        for i in range(len(dummy_path)):
            src_as = dummy_path[i]
            expected_path = dummy_path[i + 1 :]

            assert estimator.predict(src_as) == expected_path

    def test_when_there_is_peer_path_is_propagated(
        self,
        estimator: SimpleASPathEstimator,
        dummy_path: ASPath,
        mocker: MockerFixture,
    ) -> None:
        peer_as = AS(65536)

        as_rel_stub = mocker.create_autospec(ASRelGraph)
        as_rel_stub.bgp_receivers_from_as.side_effect = (
            lambda curr_as, prev_as: {peer_as} if curr_as == dummy_path[0] else set()
        )

        estimator.fit(as_rel_stub, {dummy_path})

        assert estimator.predict(peer_as) == dummy_path

    def test_when_as_is_disconnected_path_is_not_propagated(
        self,
        estimator: SimpleASPathEstimator,
        dummy_path: ASPath,
        mocker: MockerFixture,
    ) -> None:
        as_rel_stub = mocker.create_autospec(ASRelGraph)
        as_rel_stub.bgp_receivers_from_as.return_value = set()

        estimator.fit(as_rel_stub, {dummy_path})

        with pytest.raises(ASPathEstimationError):
            estimator.predict(AS(65536))

    def test_when_there_is_a_two_peer_chain_path_is_propagated_to_the_end(
        self,
        estimator: SimpleASPathEstimator,
        dummy_path: ASPath,
        mocker: MockerFixture,
    ) -> None:
        peer_as_one = AS(65540)
        peer_as_two = AS(65541)

        def effect(curr_as, prev_as):
            if curr_as == dummy_path[0]:
                return {peer_as_one}
            elif curr_as == peer_as_one:
                return {peer_as_two}
            else:
                return set()

        as_rel_stub = mocker.create_autospec(ASRelGraph)
        as_rel_stub.bgp_receivers_from_as.side_effect = effect

        estimator.fit(as_rel_stub, {dummy_path})

        assert estimator.predict(peer_as_two) == dummy_path.append(peer_as_one)

    def test_after_short_and_long_path_announcements_estimator_predicts_shortest_one(
        self,
        estimator: SimpleASPathEstimator,
        dummy_path: ASPath,
        dummy_path_two: ASPath,
        mocker: MockerFixture,
    ) -> None:
        peer_as = AS(65540)

        as_rel_stub = mocker.create_autospec(ASRelGraph)
        as_rel_stub.bgp_receivers_from_as.side_effect = (
            lambda curr_as, prev_as: {peer_as} if curr_as == dummy_path[0] else set()
        )

        estimator.fit(as_rel_stub, {dummy_path, dummy_path_two})

        assert estimator.predict(peer_as) == dummy_path
