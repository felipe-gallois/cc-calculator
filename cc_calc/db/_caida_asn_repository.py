import bz2
from copy import copy
from os import PathLike
from typing import TextIO

from cc_calc.core import (
    ASN,
    ASNLoadingError,
    ASNRepository,
)


def _tokenize(line: str) -> list[str]:
    if "#" in line:
        return []

    splits = line.split("|")
    return splits[:3]


def _collect_asns(source: TextIO) -> set[str]:
    asns = set()

    for line in source:
        tokens = _tokenize(line)

        if len(tokens) >= 2:
            asns.add(tokens[0])
            asns.add(tokens[1])

    return asns


class CaidaASNRepository(ASNRepository):
    def __init__(self, path: str | PathLike[str]) -> None:
        self._path = path
        self._asn_set: set[ASN] | None = None

    def load_all_asns(self) -> set[ASN]:
        if self._asn_set is None:
            self._asn_set = self._collect_all_asns()

        return copy(self._asn_set)

    def _collect_all_asns(self) -> set[ASN]:
        try:
            with bz2.open(self._path, mode="rt", encoding="utf-8") as text:
                world_asns = {ASN(asn) for asn in _collect_asns(text)}

            return world_asns
        except Exception as e:
            raise ASNLoadingError() from e
