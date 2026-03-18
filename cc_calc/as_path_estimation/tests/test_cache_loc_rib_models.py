import pytest
from pytest_mock import MockerFixture

from cc_calc.as_path_estimation._as_path import ASPath
from cc_calc.as_path_estimation._as_rel_graph import (
    ASRel,
    ASRelGraph,
    ASRelGraphRepository,
    ASRelGraphRepositoryError,
    RelType,
)
from cc_calc.as_path_estimation._cache_loc_rib_models import (
    CacheLocRIBModels,
    CacheLocRIBModelsError,
)
from cc_calc.as_path_estimation._loc_rib_model import LocRIBModelRepository
from cc_calc.as_path_estimation._prefix_sure_as_path_list import (
    PrefixSureASPathList,
    PrefixSureASPathListRepository,
    PrefixSureASPathListRepositoryError,
)
from cc_calc.autonomous_system import AS
from cc_calc.ip_prefix import IPPrefix
from cc_calc.logging import Logger


def test_when_model_has_two_ases_and_prefix_returns_correct_model(
    mocker: MockerFixture,
) -> None:
    rel_graph_repo_mock = mocker.create_autospec(ASRelGraphRepository)
    rel_graph_repo_mock.load_rel_graph.side_effect = lambda: ASRelGraph(
        {ASRel(AS(65536), AS(65537), RelType.P2C)}
    )

    sure_path_list_repo_mock = mocker.create_autospec(PrefixSureASPathListRepository)
    sure_path_list_repo_mock.load_all_sure_path_lists.side_effect = lambda: {
        PrefixSureASPathList(IPPrefix("192.0.2.0/24"), {ASPath([AS(65536)])})
    }

    loc_rib_model_repo_mock = mocker.create_autospec(LocRIBModelRepository)

    logger_mock = mocker.create_autospec(Logger)

    service = CacheLocRIBModels(
        rel_graph_repo_mock,
        sure_path_list_repo_mock,
        loc_rib_model_repo_mock,
        logger_mock,
    )

    service.cache_models()
    model = loc_rib_model_repo_mock.save_model.call_args[0][0]

    # assert model.best_path(AS(65536)) == ASPath([AS(65536)])
    assert model.best_path(AS(65537)) == ASPath([AS(65537), AS(65536)])


def test_when_graph_repo_raises_exception_propagate_exception(
    mocker: MockerFixture,
) -> None:
    rel_graph_repo_mock = mocker.create_autospec(ASRelGraphRepository)
    rel_graph_repo_mock.load_rel_graph.side_effect = ASRelGraphRepositoryError(
        "Repository error"
    )

    sure_path_list_repo_mock = mocker.create_autospec(PrefixSureASPathListRepository)

    loc_rib_model_repo_mock = mocker.create_autospec(LocRIBModelRepository)

    logger_mock = mocker.create_autospec(Logger)

    service = CacheLocRIBModels(
        rel_graph_repo_mock,
        sure_path_list_repo_mock,
        loc_rib_model_repo_mock,
        logger_mock,
    )

    with pytest.raises(CacheLocRIBModelsError):
        service.cache_models()


def test_when_paths_repo_raises_exception_propagate_exception(
    mocker: MockerFixture,
) -> None:
    rel_graph_repo_mock = mocker.create_autospec(ASRelGraphRepository)
    rel_graph_repo_mock.load_rel_graph.side_effect = None

    sure_path_list_repo_mock = mocker.create_autospec(PrefixSureASPathListRepository)
    sure_path_list_repo_mock.load_all_sure_path_lists.side_effect = (
        PrefixSureASPathListRepositoryError("Repository error")
    )

    loc_rib_model_repo_mock = mocker.create_autospec(LocRIBModelRepository)

    logger_mock = mocker.create_autospec(Logger)

    service = CacheLocRIBModels(
        rel_graph_repo_mock,
        sure_path_list_repo_mock,
        loc_rib_model_repo_mock,
        logger_mock,
    )

    with pytest.raises(CacheLocRIBModelsError):
        service.cache_models()
