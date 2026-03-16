import pytest

from cc_calc.as_path_estimation import (
    ASPath,
    LocRIBModel,
    LocRIBModelError,
    SecondSurePathEvent,
)
from cc_calc.autonomous_system import AS
from cc_calc.ip_prefix import IPPrefix


@pytest.fixture
def dummy_path() -> ASPath:
    return ASPath((AS(65537), AS(65538), AS(65539)))


@pytest.fixture
def dummy_path_two() -> ASPath:
    return ASPath((AS(65537), AS(65538), AS(65539), AS(65540)))


@pytest.fixture
def dummy_path_recursive(dummy_path: ASPath) -> list[ASPath]:
    return [dummy_path[i + 1 :] for i in range(len(dummy_path))]


@pytest.fixture
def model() -> LocRIBModel:
    return LocRIBModel(IPPrefix("192.0.2.0/24"))


class TestAddLocRIBPath:
    def test_querying_empty_rib_raises_exception(self, model: LocRIBModel) -> None:
        with pytest.raises(LocRIBModelError):
            model.best_path(AS(65536))

    def test_after_unsure_path_update_rib_updates_path(
        self, model: LocRIBModel, dummy_path: ASPath
    ) -> None:
        model.add_path(AS(65536), dummy_path)
        assert model.best_path(AS(65536)) == dummy_path

    def test_after_unsure_path_update_other_as_loc_rib_does_not_update(
        self, model: LocRIBModel, dummy_path: ASPath
    ) -> None:
        model.add_path(AS(65536), dummy_path)

        with pytest.raises(LocRIBModelError):
            model.best_path(AS(65537))

    def test_after_two_unsure_path_updates_best_path_is_the_shortest(
        self,
        model: LocRIBModel,
        dummy_path: ASPath,
        dummy_path_two: ASPath,
    ) -> None:
        model.add_path(AS(65536), dummy_path)
        model.add_path(AS(65536), dummy_path_two)
        assert model.best_path(AS(65536)) == dummy_path

    def test_after_sure_and_unsure_path_updates_best_path_is_the_sure_one(
        self,
        model: LocRIBModel,
        dummy_path: ASPath,
        dummy_path_two: ASPath,
    ) -> None:
        model.add_path(AS(65536), dummy_path_two, sureness=True)
        model.add_path(AS(65536), dummy_path)
        assert model.best_path(AS(65536)) == dummy_path_two

    def test_after_unsure_path_update_returns_true(
        self, model: LocRIBModel, dummy_path: ASPath
    ) -> None:
        assert model.add_path(AS(65536), dummy_path) is True

    def test_after_no_unsure_path_update_returns_false(
        self, model: LocRIBModel, dummy_path: ASPath, dummy_path_two: ASPath
    ) -> None:
        model.add_path(AS(65536), dummy_path)
        assert model.add_path(AS(65536), dummy_path_two) is False

    def test_after_unsure_path_update_following_no_update_returns_true(
        self, model: LocRIBModel, dummy_path: ASPath, dummy_path_two: ASPath
    ) -> None:
        model.add_path(AS(65536), dummy_path_two)
        model.add_path(AS(65536), dummy_path_two)
        assert model.add_path(AS(65536), dummy_path) is True


class TestGenerateEvents:
    def test_after_two_sure_path_additions_generates_event(
        self, model: LocRIBModel, dummy_path: ASPath
    ) -> None:
        model.add_path(AS(65536), dummy_path, sureness=True)
        model.add_path(AS(65536), dummy_path, sureness=True)
        assert (
            SecondSurePathEvent(
                target=AS(65536), old_path=dummy_path, new_path=dummy_path
            )
            in model.events
        )
