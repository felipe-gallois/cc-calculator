from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from cc_calc.country_code import Alpha2Code
from cc_calc.ip_block._file_ip_block_repository import FileIPBlockRepository
from cc_calc.ip_block._ip_block import IPBlock, IPBlockRepositoryError
from cc_calc.ip_block._ip_prefix_source import IPPrefixSource, IPPrefixSourceError
from cc_calc.ip_block._prefix_country_resolver import (
    PrefixCountryResolver,
    PrefixCountryResolverError,
)
from cc_calc.ip_prefix import IPPrefix


@pytest.fixture
def prefix_source(mocker: MockerFixture) -> MagicMock:
    return mocker.create_autospec(IPPrefixSource)


@pytest.fixture
def country_res(mocker: MockerFixture) -> MagicMock:
    return mocker.create_autospec(PrefixCountryResolver)


def test_when_country_has_one_block_loads_block(
    prefix_source: MagicMock,
    country_res: MagicMock,
) -> None:
    prefix_map = {
        "192.0.2.0/24": "BR",
    }

    prefix_source.load_all_ip_prefixes.return_value = set(prefix_map.keys())
    country_res.load_prefix_country.side_effect = lambda prefix: prefix_map[prefix]

    resolver = FileIPBlockRepository(prefix_source, country_res)

    country_blocks = resolver.load_blocks_in_country(Alpha2Code("BR"))

    assert country_blocks == {IPBlock(IPPrefix("192.0.2.0/24"))}


def test_when_country_has_two_blocks_loads_blocks(
    prefix_source: MagicMock,
    country_res: MagicMock,
) -> None:
    prefix_map = {
        "192.0.2.0/24": "BR",
        "198.51.100.0/24": "BR",
    }

    prefix_source.load_all_ip_prefixes.return_value = set(prefix_map.keys())
    country_res.load_prefix_country.side_effect = lambda prefix: prefix_map[prefix]

    resolver = FileIPBlockRepository(prefix_source, country_res)

    country_blocks = resolver.load_blocks_in_country(Alpha2Code("BR"))

    assert country_blocks == {
        IPBlock(IPPrefix("192.0.2.0/24")),
        IPBlock(IPPrefix("198.51.100.0/24")),
    }


def test_when_two_countries_have_one_block_each_loads_country_block(
    prefix_source: MagicMock,
    country_res: MagicMock,
) -> None:
    prefix_map = {
        "192.0.2.0/24": "BR",
        "198.51.100.0/24": "US",
    }

    prefix_source.load_all_ip_prefixes.return_value = set(prefix_map.keys())
    country_res.load_prefix_country.side_effect = lambda prefix: prefix_map[prefix]

    resolver = FileIPBlockRepository(prefix_source, country_res)

    country_blocks = resolver.load_blocks_in_country(Alpha2Code("BR"))

    assert country_blocks == {IPBlock(IPPrefix("192.0.2.0/24"))}


def test_when_there_was_an_error_loading_prefixes_propagates_error(
    prefix_source: MagicMock,
    country_res: MagicMock,
) -> None:
    prefix_source.load_all_ip_prefixes.side_effect = IPPrefixSourceError(
        "Prefix loading error"
    )

    resolver = FileIPBlockRepository(prefix_source, country_res)

    with pytest.raises(IPBlockRepositoryError):
        resolver.load_blocks_in_country(Alpha2Code("BR"))


def test_when_there_was_an_error_loading_countries_propagates_error(
    prefix_source: MagicMock,
    country_res: MagicMock,
) -> None:
    prefix_source.load_all_ip_prefixes.return_value = {"192.0.2.0/24"}
    country_res.load_prefix_country.side_effect = PrefixCountryResolverError(
        "Prefix country loading error"
    )

    resolver = FileIPBlockRepository(prefix_source, country_res)

    with pytest.raises(IPBlockRepositoryError):
        resolver.load_blocks_in_country(Alpha2Code("BR"))
