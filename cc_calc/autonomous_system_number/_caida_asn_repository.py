import bz2
from os import PathLike
from typing import TextIO

from cc_calc.autonomous_system_number._autonomous_system_number import (
    ASN,
    ASNRepository,
    ASNRepositoryError,
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

    def load_all_asns(self) -> set[ASN]:
        try:
            with bz2.open(self._path, mode="rt", encoding="utf-8") as text:
                return {ASN(asn) for asn in _collect_asns(text)}
        except Exception as e:
            raise ASNRepositoryError("Could not read input file") from e
