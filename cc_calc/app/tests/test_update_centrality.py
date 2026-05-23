from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from cc_calc.app._country_path_estimation import (
    CountryPathEstimation,
)
from cc_calc.app._update_centrality import CentralityUpdate
from cc_calc.core import (
    ASN,
    Alpha2Code,
    ASLoadingError,
    ASPath,
    CountryCode,
    CountryPath,
    IPBlock,
    IPBlockLoadingError,
    IPBlockRepository,
    IPBlockSpecification,
    IPPrefix,
)


@pytest.fixture
def ip_block_repo_mock(mocker: MockerFixture) -> MagicMock:
    def find_block_set(specs: set[IPBlockSpecification]) -> set[IPBlock]:
        if len(specs) == 2:
            return {IPBlock(IPPrefix("192.0.2.0/24"), Alpha2Code("BR"), ASN(65536))}

        if len(specs) == 1:
            return {
                IPBlock(IPPrefix("198.51.100.0/24"), Alpha2Code("CA"), ASN(65537)),
                IPBlock(IPPrefix("203.0.113.0/25"), Alpha2Code("CA"), ASN(65537)),
                IPBlock(IPPrefix("203.0.113.128/25"), Alpha2Code("US"), ASN(65537)),
            }

        return set()

    repo_mock = mocker.create_autospec(IPBlockRepository)
    repo_mock.load_blocks_with_specs.side_effect = lambda specs: find_block_set(specs)
    return repo_mock


@pytest.fixture
def country_path_estimation_mock(mocker: MockerFixture) -> MagicMock:
    as_path_map = {
        ASPath([ASN(65536)]): CountryPath([Alpha2Code("US")]),
        ASPath([ASN(65538)]): CountryPath([Alpha2Code("MX")]),
        ASPath([ASN(65539)]): CountryPath([Alpha2Code("BR")]),
    }

    estimation_mock = mocker.create_autospec(CountryPathEstimation)
    estimation_mock.estimate_country_path.side_effect = lambda as_path: as_path_map[
        as_path
    ]

    return estimation_mock


@pytest.mark.parametrize(
    "asn,expected_table",
    [
        (ASN(65536), {Alpha2Code("US"): (2**8 * (2**8 + 2**7))}),
        (ASN(65538), {Alpha2Code("MX"): (2**8 * (2**8 + 2**7 + 2**7))}),
    ],
)
def test_when_path_has_one_in_between_country_its_centrality_gets_updated(
    asn: ASN,
    expected_table: dict[CountryCode, int],
    country_path_estimation_mock: MagicMock,
    ip_block_repo_mock: MagicMock,
) -> None:
    as_path = ASPath([asn])
    src_country = Alpha2Code("BR")

    centrality_update = CentralityUpdate(
        country_path_estimation_mock, ip_block_repo_mock
    )
    centrality_table = centrality_update.execute(as_path, src_country)

    assert centrality_table.items() == expected_table.items()


def test_when_path_has_src_country_its_centrality_is_not_changed(
    country_path_estimation_mock: MagicMock,
    ip_block_repo_mock: MagicMock,
) -> None:
    as_path = ASPath([ASN(65539)])
    src_country = Alpha2Code("BR")

    centrality_update = CentralityUpdate(
        country_path_estimation_mock, ip_block_repo_mock
    )
    centrality_table = centrality_update.execute(as_path, src_country)

    assert len(centrality_table.items()) == 0


def test_when_block_repo_raises_exception_it_returns_empty_table(
    country_path_estimation_mock: MagicMock,
    ip_block_repo_mock: MagicMock,
) -> None:
    as_path = ASPath([ASN(65539)])
    src_country = Alpha2Code("BR")

    ip_block_repo_mock.load_blocks_with_specs.side_effect = IPBlockLoadingError()

    centrality_update = CentralityUpdate(
        country_path_estimation_mock, ip_block_repo_mock
    )

    centrality_table = centrality_update.execute(as_path, src_country)

    assert len(centrality_table.items()) == 0


def test_when_path_estimation_raises_exception_it_returns_empty_table(
    country_path_estimation_mock: MagicMock,
    ip_block_repo_mock: MagicMock,
) -> None:
    as_path = ASPath([ASN(65539)])
    src_country = Alpha2Code("BR")

    country_path_estimation_mock.estimate_country_path.side_effect = ASLoadingError()

    centrality_update = CentralityUpdate(
        country_path_estimation_mock, ip_block_repo_mock
    )

    centrality_table = centrality_update.execute(as_path, src_country)

    assert len(centrality_table.items()) == 0
