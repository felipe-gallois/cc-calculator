import bz2
from collections.abc import Iterator
from os import PathLike

from cc_calc.bgp_simulation import IPPrefix, RIBEntry, RIBLoader, RIBLoadingError


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

        return RIBEntry(prefix=IPPrefix(spaced_tokens[2]), as_path=as_path)
