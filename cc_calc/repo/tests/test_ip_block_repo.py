from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from cc_calc.core import (
    ASN,
    Alpha2Code,
    ASSpecification,
    CountrySpecification,
    IPBlock,
    IPPrefix,
)
from cc_calc.repo._ip_block_repo import IPBlockRepo
from cc_calc.repo._database import IPPrefixDB, PrefixASNDB, PrefixCountryDB


@pytest.fixture
def prefix_source(mocker: MockerFixture) -> MagicMock:
    return mocker.create_autospec(IPPrefixDB)


@pytest.fixture
def asn_res(mocker: MockerFixture) -> MagicMock:
    return mocker.create_autospec(PrefixASNDB)


@pytest.fixture
def country_res(mocker: MockerFixture) -> MagicMock:
    return mocker.create_autospec(PrefixCountryDB)


def test_when_country_has_one_block_loads_block(
    prefix_source: MagicMock,
    asn_res: MagicMock,
    country_res: MagicMock,
) -> None:
    prefix_map = {
        "192.0.2.0/24": (65536, "BR"),
    }

    prefix_source.load_all_ip_prefixes.return_value = set(prefix_map.keys())
    asn_res.load_prefix_asn.side_effect = lambda prefix: prefix_map[prefix][0]
    country_res.load_prefix_country.side_effect = lambda prefix: prefix_map[prefix][1]

    resolver = IPBlockRepo(prefix_source, asn_res, country_res)

    spec = CountrySpecification(Alpha2Code("BR"))
    country_blocks = resolver.load_blocks_with_specs({spec})

    assert country_blocks == {IPBlock(IPPrefix("192.0.2.0/24"))}


def test_when_country_has_two_blocks_loads_blocks(
    prefix_source: MagicMock,
    asn_res: MagicMock,
    country_res: MagicMock,
) -> None:
    prefix_map = {
        "192.0.2.0/24": (65536, "BR"),
        "198.51.100.0/24": (65536, "BR"),
    }

    prefix_source.load_all_ip_prefixes.return_value = set(prefix_map.keys())
    asn_res.load_prefix_asn.side_effect = lambda prefix: prefix_map[prefix][0]
    country_res.load_prefix_country.side_effect = lambda prefix: prefix_map[prefix][1]

    resolver = IPBlockRepo(prefix_source, asn_res, country_res)

    spec = CountrySpecification(Alpha2Code("BR"))
    country_blocks = resolver.load_blocks_with_specs({spec})

    assert country_blocks == {
        IPBlock(IPPrefix("192.0.2.0/24")),
        IPBlock(IPPrefix("198.51.100.0/24")),
    }


def test_when_two_countries_have_one_block_each_loads_country_block(
    prefix_source: MagicMock,
    asn_res: MagicMock,
    country_res: MagicMock,
) -> None:
    prefix_map = {
        "192.0.2.0/24": (65536, "BR"),
        "198.51.100.0/24": (65536, "US"),
    }

    prefix_source.load_all_ip_prefixes.return_value = set(prefix_map.keys())
    asn_res.load_prefix_asn.side_effect = lambda prefix: prefix_map[prefix][0]
    country_res.load_prefix_country.side_effect = lambda prefix: prefix_map[prefix][1]

    resolver = IPBlockRepo(prefix_source, asn_res, country_res)

    spec = CountrySpecification(Alpha2Code("BR"))
    country_blocks = resolver.load_blocks_with_specs({spec})

    assert country_blocks == {IPBlock(IPPrefix("192.0.2.0/24"))}


@pytest.mark.parametrize(
    "prefix_str, asn, country",
    [
        ("192.0.2.0/24", ASN(65536), Alpha2Code("BR")),
        ("198.51.100.0/24", ASN(65537), Alpha2Code("US")),
    ],
)
def test_when_block_is_returned_asn_and_country_are_correctly_set(
    prefix_source: MagicMock,
    asn_res: MagicMock,
    country_res: MagicMock,
    prefix_str: str,
    asn: ASN,
    country: Alpha2Code,
) -> None:
    prefix_source.load_all_ip_prefixes.return_value = {prefix_str}
    asn_res.load_prefix_asn.side_effect = lambda prefix: str(asn)
    country_res.load_prefix_country.side_effect = lambda prefix: str(country)

    resolver = IPBlockRepo(prefix_source, asn_res, country_res)

    spec = CountrySpecification(country)
    country_blocks = resolver.load_blocks_with_specs({spec})

    assert len(country_blocks) == 1
    assert list(country_blocks)[0].autonomous_system == asn
    assert list(country_blocks)[0].country == country


def test_when_loading_blocks_with_multiple_specs_returns_correct_blocks(
    prefix_source: MagicMock,
    asn_res: MagicMock,
    country_res: MagicMock,
) -> None:
    prefix_map = {
        "192.0.2.0/24": (65536, "BR"),
        "198.51.100.0/24": (65536, "US"),
        "203.0.113.0/24": (65537, "BR"),
    }

    prefix_source.load_all_ip_prefixes.return_value = set(prefix_map.keys())
    asn_res.load_prefix_asn.side_effect = lambda prefix: prefix_map[prefix][0]
    country_res.load_prefix_country.side_effect = lambda prefix: prefix_map[prefix][1]

    resolver = IPBlockRepo(prefix_source, asn_res, country_res)

    specs = {CountrySpecification(Alpha2Code("BR")), ASSpecification(ASN(65536))}
    country_blocks = resolver.load_blocks_with_specs(specs)

    assert country_blocks == {IPBlock(IPPrefix("192.0.2.0/24"))}
