from collections.abc import Iterator
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from cc_calc.app._update_centrality import CentralityUpdate
from cc_calc.core import AS, ASN, Alpha2Code, ASPath, ASWeightGraph, IPBlock, IPPrefix
from cc_calc.repo import ASRepo


@pytest.fixture
def as_repo(mocker: MockerFixture) -> Iterator[MagicMock]:
    yield mocker.create_autospec(ASRepo)


@pytest.fixture
def as_weight_graph() -> Iterator[ASWeightGraph]:
    yield ASWeightGraph()


@pytest.fixture
def service(as_repo: MagicMock) -> Iterator[CentralityUpdate]:
    yield CentralityUpdate(as_repo)


@pytest.mark.parametrize(
    "src_prefix,dst_prefix,path_country,expected_weight",
    [
        ("192.0.2.0/24", "198.51.100.0/24", "US", 2**8 * 2**8),
        ("192.0.2.0/24", "198.51.100.0/28", "MX", 2**8 * 2**4),
    ],
)
def test_when_path_country_is_not_any_of_communicating_countries_it_adds_centrality(
    src_prefix: str,
    dst_prefix: str,
    path_country: str,
    expected_weight: int,
    as_repo: MagicMock,
    as_weight_graph: ASWeightGraph,
    service: CentralityUpdate,
) -> None:
    as_repo.load_as.side_effect = lambda asn: {
        ASN(65536): AS(ASN(65536), None),
        ASN(65537): AS(ASN(65537), Alpha2Code(path_country)),
        ASN(65538): AS(ASN(65538), None),
    }[asn]

    ip_blocks = {
        IPBlock(IPPrefix(src_prefix), Alpha2Code("BR"), ASN(65536)),
        IPBlock(IPPrefix(dst_prefix), Alpha2Code("CA"), ASN(65538)),
    }

    for block in ip_blocks:
        as_weight_graph.add_ip_block(block)

    assert (
        service.execute(
            ASPath([ASN(65536), ASN(65537), ASN(65538)]),
            as_weight_graph,
            Alpha2Code("BR"),
        ).items()
        == {Alpha2Code(path_country): expected_weight}.items()
    )


def test_when_path_country_is_src_country_it_does_not_add_centrality(
    as_repo: MagicMock, as_weight_graph: ASWeightGraph, service: CentralityUpdate
) -> None:
    as_repo.load_as.side_effect = lambda asn: {
        ASN(65536): AS(ASN(65536), None),
        ASN(65537): AS(ASN(65537), Alpha2Code("US")),
        ASN(65538): AS(ASN(65538), None),
    }[asn]

    ip_blocks = {
        IPBlock(IPPrefix("192.0.2.0/24"), Alpha2Code("US"), ASN(65536)),
        IPBlock(IPPrefix("198.51.100.0/24"), Alpha2Code("CA"), ASN(65538)),
    }

    for block in ip_blocks:
        as_weight_graph.add_ip_block(block)

    assert (
        service.execute(
            ASPath([ASN(65536), ASN(65537), ASN(65538)]),
            as_weight_graph,
            Alpha2Code("US"),
        ).items()
        == {}.items()
    )


def test_when_path_country_is_dst_country_it_does_not_add_centrality(
    as_repo: MagicMock, as_weight_graph: ASWeightGraph, service: CentralityUpdate
) -> None:
    as_repo.load_as.side_effect = lambda asn: {
        ASN(65536): AS(ASN(65536), None),
        ASN(65537): AS(ASN(65537), Alpha2Code("US")),
        ASN(65538): AS(ASN(65538), None),
    }[asn]

    ip_blocks = {
        IPBlock(IPPrefix("192.0.2.0/24"), Alpha2Code("BR"), ASN(65536)),
        IPBlock(IPPrefix("198.51.100.0/24"), Alpha2Code("US"), ASN(65538)),
    }

    for block in ip_blocks:
        as_weight_graph.add_ip_block(block)

    assert (
        service.execute(
            ASPath([ASN(65536), ASN(65537), ASN(65538)]),
            as_weight_graph,
            Alpha2Code("BR"),
        ).items()
        == {}.items()
    )


def test_when_path_has_two_countries_it_adds_centrality_for_both(
    as_repo: MagicMock, as_weight_graph: ASWeightGraph, service: CentralityUpdate
) -> None:
    as_repo.load_as.side_effect = lambda asn: {
        ASN(65536): AS(ASN(65536), None),
        ASN(65537): AS(ASN(65537), Alpha2Code("MX")),
        ASN(65538): AS(ASN(65538), Alpha2Code("US")),
        ASN(65539): AS(ASN(65539), None),
    }[asn]

    ip_blocks = {
        IPBlock(IPPrefix("192.0.2.0/24"), Alpha2Code("BR"), ASN(65536)),
        IPBlock(IPPrefix("198.51.100.0/24"), Alpha2Code("CA"), ASN(65539)),
    }

    for block in ip_blocks:
        as_weight_graph.add_ip_block(block)

    assert (
        service.execute(
            ASPath([ASN(65536), ASN(65537), ASN(65538), ASN(65539)]),
            as_weight_graph,
            Alpha2Code("BR"),
        ).items()
        == {Alpha2Code("MX"): 2**8 * 2**8, Alpha2Code("US"): 2**8 * 2**8}.items()
    )


def test_when_path_country_appears_twice_it_adds_centrality_once(
    as_repo: MagicMock, as_weight_graph: ASWeightGraph, service: CentralityUpdate
) -> None:
    as_repo.load_as.side_effect = lambda asn: {
        ASN(65537): AS(ASN(65537), None),
        ASN(65538): AS(ASN(65538), Alpha2Code("US")),
        ASN(65539): AS(ASN(65539), Alpha2Code("US")),
        ASN(65540): AS(ASN(65540), None),
    }[asn]

    ip_blocks = {
        IPBlock(IPPrefix("192.0.2.0/24"), Alpha2Code("BR"), ASN(65537)),
        IPBlock(IPPrefix("198.51.100.0/24"), Alpha2Code("CA"), ASN(65540)),
    }

    for block in ip_blocks:
        as_weight_graph.add_ip_block(block)

    assert (
        service.execute(
            ASPath([ASN(65537), ASN(65538), ASN(65539), ASN(65540)]),
            as_weight_graph,
            Alpha2Code("BR"),
        ).items()
        == {Alpha2Code("US"): 2**8 * 2**8}.items()
    )


def test_when_as_repo_raises_exception_it_does_not_add_centrality(
    as_repo: MagicMock, as_weight_graph: ASWeightGraph, service: CentralityUpdate
) -> None:
    def as_map(asn: ASN) -> AS:
        if asn == ASN(65537):
            return AS(ASN(65537), None)
        elif asn == ASN(65538):
            raise KeyError()
        else:
            return AS(ASN(65539), None)

    as_repo.load_as.side_effect = as_map

    ip_blocks = {
        IPBlock(IPPrefix("192.0.2.0/24"), Alpha2Code("BR"), ASN(65537)),
        IPBlock(IPPrefix("198.51.100.0/24"), Alpha2Code("CA"), ASN(65539)),
    }

    for block in ip_blocks:
        as_weight_graph.add_ip_block(block)

    assert (
        service.execute(
            ASPath([ASN(65537), ASN(65538), ASN(65539)]),
            as_weight_graph,
            Alpha2Code("BR"),
        ).items()
        == {}.items()
    )


@pytest.mark.parametrize(
    "second_prefix, centrality",
    [("198.51.100.0/24", 2**8 * 2**8), ("198.51.100.0/28", 2**8 * 2**4)],
)
def test_when_executed_global_centrality_sum_of_weights_to_destinations(
    second_prefix: str,
    centrality: int,
    as_repo: MagicMock,
    as_weight_graph: ASWeightGraph,
    service: CentralityUpdate,
) -> None:
    as_repo.load_as.side_effect = lambda asn: {
        ASN(65536): AS(ASN(65536), Alpha2Code("BR")),
        ASN(65537): AS(ASN(65537), Alpha2Code("AR")),
    }[asn]

    ip_blocks = {
        IPBlock(IPPrefix("192.0.2.0/24"), Alpha2Code("BR"), ASN(65536)),
        IPBlock(IPPrefix(second_prefix), Alpha2Code("AR"), ASN(65537)),
    }

    for block in ip_blocks:
        as_weight_graph.add_ip_block(block)

    centralities = service.execute(
        ASPath([ASN(65536), ASN(65537)]),
        as_weight_graph,
        Alpha2Code("BR"),
    )

    assert centralities.get_global() == centrality


@pytest.mark.parametrize(
    "src_country,src_prefix,weight",
    [("BR", "192.0.2.0/24", 2**8 * 2**8), ("CO", "192.0.2.0/28", 2**4 * 2**8)],
)
def test_when_path_country_is_src_it_is_excused(
    src_country: str,
    src_prefix: str,
    weight: int,
    as_repo: MagicMock,
    as_weight_graph: ASWeightGraph,
    service: CentralityUpdate,
) -> None:
    as_repo.load_as.side_effect = lambda asn: {
        ASN(65536): AS(ASN(65536), Alpha2Code(src_country)),
        ASN(65537): AS(ASN(65537), Alpha2Code("AR")),
    }[asn]

    ip_blocks = {
        IPBlock(IPPrefix(src_prefix), Alpha2Code(src_country), ASN(65536)),
        IPBlock(IPPrefix("198.51.100.0/24"), Alpha2Code("AR"), ASN(65537)),
    }

    for block in ip_blocks:
        as_weight_graph.add_ip_block(block)

    centralities = service.execute(
        ASPath([ASN(65536), ASN(65537)]),
        as_weight_graph,
        Alpha2Code(src_country),
    )

    assert centralities.get_excused(Alpha2Code(src_country)) == weight


@pytest.mark.parametrize(
    "dst_country,dst_prefix,weight",
    [("MX", "198.51.100.0/24", 2**8 * 2**8), ("CA", "198.51.100.0/28", 2**4 * 2**8)],
)
def test_when_path_country_is_dst_it_is_excused(
    dst_country: str,
    dst_prefix: str,
    weight: int,
    as_repo: MagicMock,
    as_weight_graph: ASWeightGraph,
    service: CentralityUpdate,
) -> None:
    as_repo.load_as.side_effect = lambda asn: {
        ASN(65536): AS(ASN(65536), Alpha2Code("BR")),
        ASN(65537): AS(ASN(65537), Alpha2Code(dst_country)),
    }[asn]

    ip_blocks = {
        IPBlock(IPPrefix("192.0.2.0/24"), Alpha2Code("BR"), ASN(65536)),
        IPBlock(IPPrefix(dst_prefix), Alpha2Code(dst_country), ASN(65537)),
    }

    for block in ip_blocks:
        as_weight_graph.add_ip_block(block)

    centralities = service.execute(
        ASPath([ASN(65536), ASN(65537)]),
        as_weight_graph,
        Alpha2Code("BR"),
    )

    assert centralities.get_excused(Alpha2Code(dst_country)) == weight


def test_when_country_intercepts_two_dst_blocks_it_gains_centrality_from_both(
    as_repo: MagicMock,
    as_weight_graph: ASWeightGraph,
    service: CentralityUpdate,
) -> None:
    as_repo.load_as.side_effect = lambda asn: {
        ASN(65536): AS(ASN(65536), Alpha2Code("BR")),
        ASN(65537): AS(ASN(65537), Alpha2Code("US")),
        ASN(65538): AS(ASN(65538), Alpha2Code("CA")),
    }[asn]

    ip_blocks = {
        IPBlock(IPPrefix("192.0.2.0/24"), Alpha2Code("BR"), ASN(65536)),
        IPBlock(IPPrefix("198.51.100.0/24"), Alpha2Code("CA"), ASN(65538)),
        IPBlock(IPPrefix("203.0.113.0/24"), Alpha2Code("MX"), ASN(65538)),
    }

    for block in ip_blocks:
        as_weight_graph.add_ip_block(block)

    centralities = service.execute(
        ASPath([ASN(65536), ASN(65537), ASN(65538)]),
        as_weight_graph,
        Alpha2Code("BR"),
    )

    assert centralities.get(Alpha2Code("US")) == 2**8 * 2**8 + 2**8 * 2**8
