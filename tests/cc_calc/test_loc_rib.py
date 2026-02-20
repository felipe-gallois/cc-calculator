import pytest

from cc_calc.autonomous_system import AS, ASPath
from cc_calc.loc_rib import LocRIBManagerError, SimpleLocRIBManager


class TestUpdateSimpleLocRIB:
    @pytest.fixture
    def dummy_path(self) -> ASPath:
        return ASPath((AS(65537), AS(65538), AS(65539)))

    @pytest.fixture
    def dummy_path_two(self) -> ASPath:
        return ASPath((AS(65537), AS(65538), AS(65539), AS(65540)))

    @pytest.fixture
    def dummy_path_recursive(self, dummy_path: ASPath) -> list[ASPath]:
        return [dummy_path[i + 1 :] for i in range(len(dummy_path))]

    @pytest.fixture
    def manager(self) -> SimpleLocRIBManager:
        return SimpleLocRIBManager()

    def test_when_created_instance_updated_is_false(
        self, manager: SimpleLocRIBManager
    ) -> None:
        assert manager.performed_unsure_update is False

    def test_querying_empty_rib_raises_exception(
        self, manager: SimpleLocRIBManager
    ) -> None:
        with pytest.raises(LocRIBManagerError):
            manager.best_path(AS(65536))

    def test_after_unsure_path_update_rib_updates_path(
        self, manager: SimpleLocRIBManager, dummy_path: ASPath
    ) -> None:
        manager.eval_unsure_path(AS(65536), dummy_path)
        assert manager.best_path(AS(65536)) == dummy_path

    def test_after_unsure_path_update_updated_is_true(
        self, manager: SimpleLocRIBManager, dummy_path: ASPath
    ) -> None:
        manager.eval_unsure_path(AS(65536), dummy_path)
        assert manager.performed_unsure_update is True

    def test_after_no_unsure_path_update_updated_is_false(
        self, manager: SimpleLocRIBManager, dummy_path: ASPath, dummy_path_two: ASPath
    ) -> None:
        manager.eval_unsure_path(AS(65536), dummy_path)
        manager.eval_unsure_path(AS(65536), dummy_path_two)
        assert manager.performed_unsure_update is False

    def test_after_unsure_path_update_following_no_update_updated_is_true(
        self, manager: SimpleLocRIBManager, dummy_path: ASPath, dummy_path_two: ASPath
    ) -> None:
        manager.eval_unsure_path(AS(65536), dummy_path_two)
        manager.eval_unsure_path(AS(65536), dummy_path_two)
        manager.eval_unsure_path(AS(65536), dummy_path)
        assert manager.performed_unsure_update is True

    def test_after_unsure_path_update_other_as_loc_rib_does_not_update(
        self, manager: SimpleLocRIBManager, dummy_path: ASPath
    ) -> None:
        manager.eval_unsure_path(AS(65536), dummy_path)

        with pytest.raises(LocRIBManagerError):
            manager.best_path(AS(65537))

    def test_after_two_unsure_path_updates_best_path_is_the_shortest(
        self,
        manager: SimpleLocRIBManager,
        dummy_path: ASPath,
        dummy_path_two: ASPath,
    ) -> None:
        manager.eval_unsure_path(AS(65536), dummy_path)
        manager.eval_unsure_path(AS(65536), dummy_path_two)
        assert manager.best_path(AS(65536)) == dummy_path

    def test_after_sure_and_unsure_path_updates_best_path_is_the_sure_one(
        self,
        manager: SimpleLocRIBManager,
        dummy_path: ASPath,
        dummy_path_two: ASPath,
    ) -> None:
        manager._eval_sure_path(AS(65536), dummy_path_two)
        manager.eval_unsure_path(AS(65536), dummy_path)
        assert manager.best_path(AS(65536)) == dummy_path_two

    def test_recursive_path_eval_updates_loc_ribs_recursively(
        self,
        manager: SimpleLocRIBManager,
        dummy_path: ASPath,
        dummy_path_recursive: list[ASPath],
    ) -> None:
        manager.eval_sure_path_recursively(dummy_path)

        for _as, path in zip(dummy_path, dummy_path_recursive):
            assert manager.best_path(_as) == path
