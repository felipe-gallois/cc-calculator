from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from cc_calc.core import (
    ASN,
    ASPath,
    ASRel,
    ASRelGraph,
    ASRelGraphRepository,
    ASRelGraphRepositoryError,
    RelType,
)
from cc_calc.app._as_path_calculation import (
    ASPathCalculation,
    ASPathCalculationError,
)


@pytest.fixture
def as_rel_graph_repo_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.create_autospec(ASRelGraphRepository)


@pytest.mark.parametrize(
    "src_as,dst_as,rels,expected_path",
    [
        (
            ASN(65536),
            ASN(65537),
            {ASRel(ASN(65536), ASN(65537), RelType.P2C)},
            ASPath([ASN(65536), ASN(65537)]),
        ),
        (
            ASN(65536),
            ASN(65538),
            {
                ASRel(ASN(65536), ASN(65537), RelType.P2C),
                ASRel(ASN(65537), ASN(65538), RelType.P2C),
            },
            ASPath([ASN(65536), ASN(65537), ASN(65538)]),
        ),
    ],
)
def test_when_graph_calculates_path_successfully_returns_path(
    src_as: ASN,
    dst_as: ASN,
    rels: set[ASRel],
    expected_path: ASPath,
    as_rel_graph_repo_mock: MagicMock,
) -> None:
    graph = ASRelGraph()
    for rel in rels:
        graph.add_rel(rel)

    as_rel_graph_repo_mock.load_rel_graph.return_value = graph

    as_path_calculation = ASPathCalculation(as_rel_graph_repo_mock)

    estimated_path = as_path_calculation.estimate_as_path(src_as, dst_as)

    assert estimated_path == expected_path


def test_when_repository_fails_to_load_graph_raises_exception(
    as_rel_graph_repo_mock: MagicMock,
) -> None:
    as_rel_graph_repo_mock.load_rel_graph.side_effect = ASRelGraphRepositoryError

    as_path_calculation = ASPathCalculation(as_rel_graph_repo_mock)

    with pytest.raises(ASPathCalculationError):
        as_path_calculation.estimate_as_path(ASN(65536), ASN(65537))


def test_when_graph_raises_exception_propagates_it(
    as_rel_graph_repo_mock: MagicMock,
) -> None:
    graph = ASRelGraph()
    as_rel_graph_repo_mock.load_rel_graph.return_value = graph

    as_path_calculation = ASPathCalculation(as_rel_graph_repo_mock)

    with pytest.raises(ASPathCalculationError):
        as_path_calculation.estimate_as_path(ASN(65536), ASN(65537))
