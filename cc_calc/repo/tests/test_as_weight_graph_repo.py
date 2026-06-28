from collections.abc import Iterator
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from cc_calc.core import ASN, Alpha2Code
from cc_calc.repo._as_weight_graph_repo import ASWeightGraphRepo
from cc_calc.repo._database import IPPrefixDB, PrefixASNDB, PrefixCountryDB


@pytest.fixture
def prefix_db_mock(mocker: MockerFixture) -> Iterator[MagicMock]:
    mock = mocker.create_autospec(IPPrefixDB, instance=True)
    mock.load_all_ip_prefixes.return_value = set()
    yield mock


@pytest.fixture
def asn_db_mock(mocker: MockerFixture) -> Iterator[MagicMock]:
    mock = mocker.create_autospec(PrefixASNDB, instance=True)
    mock.load_prefix_asn.return_value = None
    yield mock


@pytest.fixture
def country_db_mock(mocker: MockerFixture) -> Iterator[MagicMock]:
    mock = mocker.create_autospec(PrefixCountryDB, instance=True)
    mock.load_prefix_country.return_value = None
    yield mock


@pytest.fixture
def repo(
    prefix_db_mock: MagicMock, asn_db_mock: MagicMock, country_db_mock: MagicMock
) -> Iterator[ASWeightGraphRepo]:
    yield ASWeightGraphRepo(prefix_db_mock, asn_db_mock, country_db_mock)


def test_when_prefix_source_returns_no_prefix_it_returns_null_weight_graph(
    repo: ASWeightGraphRepo,
) -> None:
    graph = repo.load_weight_graph()
    assert graph.is_null()


@pytest.mark.parametrize(
    "ip_prefix_dto,asn_dto,country_dto",
    [
        ("192.0.2.0/24", 65536, "BR"),
        ("198.51.100.0/24", 65537, "US"),
    ],
)
def test_when_source_returns_prefix_and_resolvers_return_not_none_it_returns_graph(
    ip_prefix_dto: str,
    asn_dto: int,
    country_dto: str,
    prefix_db_mock: MagicMock,
    asn_db_mock: MagicMock,
    country_db_mock: MagicMock,
    repo: ASWeightGraphRepo,
) -> None:
    prefix_db_mock.load_all_ip_prefixes.return_value = {ip_prefix_dto}
    asn_db_mock.load_prefix_asn.return_value = asn_dto
    country_db_mock.load_prefix_country.return_value = country_dto

    graph = repo.load_weight_graph()
    assert graph.get_as_weights(ASN(asn_dto)) == {Alpha2Code(country_dto): 2**8}


def test_when_source_returns_prefix_and_asn_resolver_returns_none_it_returns_graph(
    prefix_db_mock: MagicMock,
    asn_db_mock: MagicMock,
    country_db_mock: MagicMock,
    repo: ASWeightGraphRepo,
) -> None:
    prefix_db_mock.load_all_ip_prefixes.return_value = {"192.0.2.0/24"}
    asn_db_mock.load_prefix_asn.return_value = None
    country_db_mock.load_prefix_country.return_value = "BR"

    graph = repo.load_weight_graph()
    assert graph.is_null()


def test_when_source_returns_prefix_and_country_resolver_returns_none_it_returns_graph(
    prefix_db_mock: MagicMock,
    asn_db_mock: MagicMock,
    country_db_mock: MagicMock,
    repo: ASWeightGraphRepo,
) -> None:
    prefix_db_mock.load_all_ip_prefixes.return_value = {"192.0.2.0/24"}
    asn_db_mock.load_prefix_asn.return_value = 65536
    country_db_mock.load_prefix_country.return_value = None

    graph = repo.load_weight_graph()
    assert graph.is_null()


def test_when_source_returns_two_prefixes_it_returns_graph_with_sum_of_both_weights(
    prefix_db_mock: MagicMock,
    asn_db_mock: MagicMock,
    country_db_mock: MagicMock,
    repo: ASWeightGraphRepo,
) -> None:
    prefix_db_mock.load_all_ip_prefixes.return_value = {
        "192.0.2.0/24",
        "198.51.100.0/28",
    }
    asn_db_mock.load_prefix_asn.return_value = 65536
    country_db_mock.load_prefix_country.return_value = "BR"

    graph = repo.load_weight_graph()
    assert graph.get_as_weights(ASN(65536)) == {Alpha2Code("BR"): 2**8 + 2**4}


def test_when_prefixes_have_different_ases_and_countries_it_returns_graph(
    prefix_db_mock: MagicMock,
    asn_db_mock: MagicMock,
    country_db_mock: MagicMock,
    repo: ASWeightGraphRepo,
) -> None:
    prefix_db_mock.load_all_ip_prefixes.return_value = {
        "192.0.2.0/24",
        "198.51.100.0/28",
    }
    asn_db_mock.load_prefix_asn.side_effect = lambda prefix: (
        65536 if prefix == "192.0.2.0/24" else 65537
    )
    country_db_mock.load_prefix_country.side_effect = lambda prefix: (
        "BR" if prefix == "192.0.2.0/24" else "US"
    )

    graph = repo.load_weight_graph()
    assert graph.get_as_weights(ASN(65536)) == {Alpha2Code("BR"): 2**8}
    assert graph.get_as_weights(ASN(65537)) == {Alpha2Code("US"): 2**4}
