from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from cc_calc.country._asn_resolver import ASNResolverError, FileASNResolver
from cc_calc.country._ip_prefix_source import IPPrefixSource, IPPrefixSourceError
from cc_calc.country._prefix_asn_resolver import (
    PrefixASNResolver,
    PrefixASNResolverError,
)
from cc_calc.country._prefix_country_resolver import (
    PrefixCountryResolver,
    PrefixCountryResolverError,
)


@pytest.fixture
def prefix_source(mocker: MockerFixture) -> MagicMock:
    return mocker.create_autospec(IPPrefixSource)


@pytest.fixture
def asn_res(mocker: MockerFixture) -> MagicMock:
    return mocker.create_autospec(PrefixASNResolver)


@pytest.fixture
def country_res(mocker: MockerFixture) -> MagicMock:
    return mocker.create_autospec(PrefixCountryResolver)


def test_when_country_has_one_as_loads_asn(
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

    resolver = FileASNResolver(prefix_source, asn_res, country_res)

    country_ases = resolver.load_country_asns("BR")

    assert country_ases == {65536}


def test_when_country_has_two_ases_loads_asns(
    prefix_source: MagicMock,
    asn_res: MagicMock,
    country_res: MagicMock,
) -> None:
    prefix_map = {
        "192.0.2.0/24": (65536, "BR"),
        "198.51.100.0/24": (65537, "BR"),
    }

    prefix_source.load_all_ip_prefixes.return_value = set(prefix_map.keys())
    asn_res.load_prefix_asn.side_effect = lambda prefix: prefix_map[prefix][0]
    country_res.load_prefix_country.side_effect = lambda prefix: prefix_map[prefix][1]

    resolver = FileASNResolver(prefix_source, asn_res, country_res)

    country_ases = resolver.load_country_asns("BR")

    assert country_ases == {65536, 65537}


def test_when_two_countries_have_one_as_each_loads_country_asn(
    prefix_source: MagicMock,
    asn_res: MagicMock,
    country_res: MagicMock,
) -> None:
    prefix_map = {
        "192.0.2.0/24": (65536, "BR"),
        "198.51.100.0/24": (65537, "US"),
    }

    prefix_source.load_all_ip_prefixes.return_value = set(prefix_map.keys())
    asn_res.load_prefix_asn.side_effect = lambda prefix: prefix_map[prefix][0]
    country_res.load_prefix_country.side_effect = lambda prefix: prefix_map[prefix][1]

    resolver = FileASNResolver(prefix_source, asn_res, country_res)

    country_ases = resolver.load_country_asns("BR")

    assert country_ases == {65536}


def test_when_only_country_prefix_has_unknown_as_does_not_load_asns(
    prefix_source: MagicMock,
    asn_res: MagicMock,
    country_res: MagicMock,
) -> None:
    prefix_map = {
        "192.0.2.0/24": (None, "BR"),
    }

    prefix_source.load_all_ip_prefixes.return_value = set(prefix_map.keys())
    asn_res.load_prefix_asn.side_effect = lambda prefix: prefix_map[prefix][0]
    country_res.load_prefix_country.side_effect = lambda prefix: prefix_map[prefix][1]

    resolver = FileASNResolver(prefix_source, asn_res, country_res)

    country_ases = resolver.load_country_asns("BR")

    assert country_ases == set()


def test_when_there_was_an_error_loading_prefixes_propagates_error(
    prefix_source: MagicMock,
    asn_res: MagicMock,
    country_res: MagicMock,
) -> None:
    prefix_source.load_all_ip_prefixes.side_effect = IPPrefixSourceError(
        "Prefix loading error"
    )

    resolver = FileASNResolver(prefix_source, asn_res, country_res)

    with pytest.raises(ASNResolverError):
        resolver.load_country_asns("BR")


def test_when_there_was_an_error_loading_asns_propagates_error(
    prefix_source: MagicMock,
    asn_res: MagicMock,
    country_res: MagicMock,
) -> None:
    prefix_source.load_all_ip_prefixes.return_value = {"192.0.2.0/24"}
    asn_res.load_prefix_asn.side_effect = PrefixASNResolverError(
        "Prefix ASN loading error"
    )

    resolver = FileASNResolver(prefix_source, asn_res, country_res)

    with pytest.raises(ASNResolverError):
        resolver.load_country_asns("BR")


def test_when_there_was_an_error_loading_countries_propagates_error(
    prefix_source: MagicMock,
    asn_res: MagicMock,
    country_res: MagicMock,
) -> None:
    prefix_source.load_all_ip_prefixes.return_value = {"192.0.2.0/24"}
    asn_res.load_prefix_asn.return_value = 65536
    country_res.load_prefix_country.side_effect = PrefixCountryResolverError(
        "Prefix country loading error"
    )

    resolver = FileASNResolver(prefix_source, asn_res, country_res)

    with pytest.raises(ASNResolverError):
        resolver.load_country_asns("BR")
