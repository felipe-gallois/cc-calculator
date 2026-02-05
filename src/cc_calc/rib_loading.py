import bz2

from collections.abc import Iterator
from ipaddress import ip_network, IPv4Network
from os import PathLike
from typing import TextIO

from cc_calc.bgp_simulation import RIBEntry, RIBLoader, RIBLoadingError


class CaidaRIBLoader(RIBLoader):
    def __init__(self, path: str | PathLike[str]) -> None:
        self._path = path

    def iter(self) -> Iterator[RIBEntry]:
        try:
            with bz2.open(self._path, "rt") as text:
                for line in text:
                    yield CaidaRIBLoader._parse_entry(line)
        except Exception as e:
            raise RIBLoadingError("Could not read input file") from e

    @staticmethod
    def _parse_entry(line: str) -> RIBEntry:
        spaced_tokens = line.split(" ")

        as_path = spaced_tokens[1].split("|")

        return RIBEntry(prefix=ip_network(spaced_tokens[2]), as_path=as_path)
