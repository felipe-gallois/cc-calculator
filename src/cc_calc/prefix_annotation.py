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
    with Reader(as_file) as reader:
        return {
            prefix: reader.asn(prefix.network_address).autonomous_system_number
            for prefix in prefixes
        }


def get_prefixes_countries(
        prefixes: Iterable[IPv4Network],
        countries_file: str | PathLike[str]
) -> dict[IPv4Network, Country | None]:
    with Reader(countries_file) as reader:
        return {
            prefix: reader.country(prefix.network_address).country.iso_code
            for prefix in prefixes
        }
