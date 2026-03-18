import bz2
from os import PathLike
from typing import TextIO

from cc_calc.ip_prefix._ip_prefix import (
    IPPrefix,
    IPPrefixRepository,
    IPPrefixRepositoryError,
)


def _collect_prefixes(text: TextIO) -> set[str]:
    prefixes: set[str] = set()

    for line in text:
        spaced_tokens = line.split(" ")
        prefix = spaced_tokens[2]
        prefixes.add(prefix)

    return prefixes


class CaidaIPPrefixRepository(IPPrefixRepository):
    def __init__(self, path: str | PathLike[str]) -> None:
        self._path = path

    def load_prefixes(self) -> set[IPPrefix]:
        try:
            with bz2.open(self._path, "rt") as text:
                prefixes = _collect_prefixes(text)
                return {IPPrefix(prefix) for prefix in prefixes}
        except Exception as e:
            raise IPPrefixRepositoryError("Could not read input file") from e
