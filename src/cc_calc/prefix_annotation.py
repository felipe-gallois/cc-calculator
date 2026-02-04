"""Queries MaxMind's databases to find properties of IP prefixes."""

from collections.abc import Iterable
from ipaddress import IPv4Network
from os import PathLike
from typing import TypeAlias

from geoip2.database import Reader

ASN: TypeAlias = int
Country: TypeAlias = str


def get_prefixes_asns(
    prefixes: Iterable[IPv4Network],
    as_file: str | PathLike[str],
) -> dict[IPv4Network, ASN | None]:
    """Get the autonomous system numbers of a collection of IPv4 prefixes.

    Assumes that prefixes are small enough to reside in only one country each.

    Args:
        prefixes: A collection of IPv4 prefixes.
        as_file: The path to MaxMind's ASN database file.

    Returns: A mapping of IPv4 prefixes to ASNs.
    """
    with Reader(as_file) as reader:
        return {
            prefix: reader.asn(prefix.network_address).autonomous_system_number
            for prefix in prefixes
        }


def get_prefixes_countries(
    prefixes: Iterable[IPv4Network], countries_file: str | PathLike[str]
) -> dict[IPv4Network, Country | None]:
    """Get the countries of a collection of IPv4 prefixes.

    Assumes that prefixes are small enough to reside in only one country each.

    Args:
        prefixes: A collection of IPv4 prefixes.
        countries_file: The path to MaxMind's countries database file.

    Returns: A mapping of IPv4 prefixes to ASNs.
    """
    with Reader(countries_file) as reader:
        return {
            prefix: reader.country(prefix.network_address).country.iso_code
            for prefix in prefixes
        }
