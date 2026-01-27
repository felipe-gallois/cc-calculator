import bz2
import re
from ipaddress import IPv4Network
from os import PathLike
from typing import TextIO


def collect_compressed_prefixes(path: str | PathLike[str]) -> set[IPv4Network]:
    with bz2.open(path, mode="rt", encoding="utf-8") as text:
        return _collect_prefixes(text)


def _collect_prefixes(source: TextIO) -> set[IPv4Network]:
    prefixes = set()

    for line in source:
        prefix_str = re.search(r"(?:\d{1,3}\.){3}\d{1,3}/\d{1,2}", line)

        if prefix_str:
            prefix = IPv4Network(prefix_str.group(0))
            prefixes.add(prefix)

    return prefixes
