from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from cc_calc.app._centrality_calculation import CentralityCalculation
from cc_calc.app._update_centrality import CentralityUpdate
from cc_calc.core import (
    ASN,
    Alpha2Code,
    ASPath,
    ASRelGraph,
    CentralityTable,
    CountryCode,
    CountrySpecification,
    IPBlock,
    IPPrefix,
)
from cc_calc.repo import ASNRepo, ASRelGraphRepo, IPBlockRepo

DEFAULT_COUNTRY_BLOCKS = {
    IPBlock(IPPrefix("192.0.2.0/24"), Alpha2Code("BR"), ASN(65536))
}

DEFAULT_WORLD_ASNS = {ASN(65536), ASN(65537)}

DEFAULT_AS_PATH_MAP = {
    (ASN(65536), ASN(65536)): ASPath([ASN(65536)]),
    (ASN(65536), ASN(65537)): ASPath([ASN(65536), ASN(65537)]),
}

DEFAULT_CENTRALITY_MAP = {
    ASPath([ASN(65536)]): CentralityTable(),
    ASPath([ASN(65536), ASN(65537)]): CentralityTable({Alpha2Code("US"): 50}),
}

DEFAULT_CENTRALITIES = {Alpha2Code("US"): 50}

test_data = [
    (
        DEFAULT_COUNTRY_BLOCKS,
        DEFAULT_WORLD_ASNS,
        DEFAULT_AS_PATH_MAP,
        DEFAULT_CENTRALITY_MAP,
        DEFAULT_CENTRALITIES,
    ),
    (
        DEFAULT_COUNTRY_BLOCKS,
        DEFAULT_WORLD_ASNS,
        DEFAULT_AS_PATH_MAP,
        {
            ASPath([ASN(65536)]): CentralityTable(),
            ASPath([ASN(65536), ASN(65537)]): CentralityTable({Alpha2Code("US"): 100}),
        },
        {Alpha2Code("US"): 100},
    ),
    (
        DEFAULT_COUNTRY_BLOCKS,
        {ASN(65536), ASN(65538)},
        {
            (ASN(65536), ASN(65536)): ASPath([ASN(65536)]),
            (ASN(65536), ASN(65538)): ASPath([ASN(65536), ASN(65538)]),
        },
        {
            ASPath([ASN(65536)]): CentralityTable(),
            ASPath([ASN(65536), ASN(65538)]): CentralityTable({Alpha2Code("US"): 50}),
        },
        DEFAULT_CENTRALITIES,
    ),
    (
        DEFAULT_COUNTRY_BLOCKS,
        {ASN(65536), ASN(65537), ASN(65538)},
        {
            (ASN(65536), ASN(65536)): ASPath([ASN(65536)]),
            (ASN(65536), ASN(65537)): ASPath([ASN(65536), ASN(65537)]),
            (ASN(65536), ASN(65538)): ASPath([ASN(65536), ASN(65538)]),
        },
        {
            ASPath([ASN(65536)]): CentralityTable(),
            ASPath([ASN(65536), ASN(65537)]): CentralityTable(),
            ASPath([ASN(65536), ASN(65538)]): CentralityTable({Alpha2Code("US"): 50}),
        },
        DEFAULT_CENTRALITIES,
    ),
    (
        DEFAULT_COUNTRY_BLOCKS,
        {ASN(65536), ASN(65537), ASN(65538)},
        {
            (ASN(65536), ASN(65536)): ASPath([ASN(65536)]),
            (ASN(65536), ASN(65537)): ASPath([ASN(65536), ASN(65537)]),
            (ASN(65536), ASN(65538)): ASPath([ASN(65536), ASN(65538)]),
            (ASN(65537), ASN(65538)): ASPath([ASN(65537), ASN(65538)]),
        },
        {
            ASPath([ASN(65536)]): CentralityTable(),
            ASPath([ASN(65536), ASN(65537)]): CentralityTable(),
            ASPath([ASN(65536), ASN(65538)]): CentralityTable({Alpha2Code("US"): 50}),
            ASPath([ASN(65537), ASN(65538)]): CentralityTable({Alpha2Code("US"): 50}),
        },
        DEFAULT_CENTRALITIES,
    ),
]


@pytest.fixture
def ip_block_repo_mock(
    mocker: MockerFixture, request: pytest.FixtureRequest
) -> MagicMock:
    repo_mock = mocker.create_autospec(IPBlockRepo)
    repo_mock.load_blocks_with_specs.return_value = request.param
    return repo_mock


@pytest.fixture
def asn_repo_mock(mocker: MockerFixture, request: pytest.FixtureRequest) -> MagicMock:
    asn_repo_mock = mocker.create_autospec(ASNRepo)
    asn_repo_mock.load_all_asns.return_value = request.param
    return asn_repo_mock


@pytest.fixture
def rel_graph_repo_mock(
    mocker: MockerFixture, request: pytest.FixtureRequest
) -> MagicMock:
    rel_graph_mock = mocker.create_autospec(ASRelGraph)
    rel_graph_mock.get_as_path.side_effect = lambda src_as, dst_as: request.param[
        src_as, dst_as
    ]

    rel_graph_mock.clone.return_value = rel_graph_mock

    rel_graph_repo_mock = mocker.create_autospec(ASRelGraphRepo)
    rel_graph_repo_mock.load_rel_graph.return_value = rel_graph_mock

    return rel_graph_repo_mock


@pytest.fixture
def update_mock(mocker: MockerFixture, request: pytest.FixtureRequest) -> MagicMock:
    centrality_update = mocker.create_autospec(CentralityUpdate)
    centrality_update.execute.side_effect = lambda as_path, _: request.param[as_path]
    return centrality_update


@pytest.mark.parametrize(
    "ip_block_repo_mock,asn_repo_mock,rel_graph_repo_mock,update_mock,exp_centralities",
    test_data,
    indirect=[
        "ip_block_repo_mock",
        "asn_repo_mock",
        "rel_graph_repo_mock",
        "update_mock",
    ],
)
def test_calculates_combined_centralities_of_src_and_dst_pairs(
    ip_block_repo_mock: MagicMock,
    asn_repo_mock: MagicMock,
    rel_graph_repo_mock: MagicMock,
    update_mock: MagicMock,
    exp_centralities: dict[CountryCode, int],
) -> None:
    pivot_country = Alpha2Code("BR")

    centrality_calculation = CentralityCalculation(
        ip_block_repo_mock, asn_repo_mock, rel_graph_repo_mock, update_mock
    )

    centralities = centrality_calculation.execute(pivot_country)

    assert centralities.items() == exp_centralities.items()


@pytest.mark.parametrize(
    "pivot_country,ip_block_repo_mock,asn_repo_mock,rel_graph_repo_mock,update_mock",
    [(Alpha2Code("BR"), *test_data[0][:4]), (Alpha2Code("US"), *test_data[0][:4])],
    indirect=[
        "ip_block_repo_mock",
        "asn_repo_mock",
        "rel_graph_repo_mock",
        "update_mock",
    ],
)
def test_ip_block_repo_is_called_with_correct_specs(
    pivot_country: CountryCode,
    ip_block_repo_mock: MagicMock,
    asn_repo_mock: MagicMock,
    rel_graph_repo_mock: MagicMock,
    update_mock: MagicMock,
) -> None:
    centrality_calculation = CentralityCalculation(
        ip_block_repo_mock, asn_repo_mock, rel_graph_repo_mock, update_mock
    )

    centrality_calculation.execute(pivot_country)

    ip_block_repo_mock.load_blocks_with_specs.assert_called_with(
        {CountrySpecification(pivot_country)}
    )
