import bz2
import logging
from os import PathLike
from typing import TextIO

from cc_calc.core import (
    ASN,
    ASNLoadingError,
    ASNRepository,
)

logger = logging.getLogger(__name__)


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
                world_asns = {ASN(asn) for asn in _collect_asns(text)}

            logger.info("Loaded world ASNs")

            return world_asns
        except Exception as e:
            message = "Failed loading world ASNs: could not read input file"
            logger.error(message)
            raise ASNLoadingError(message) from e
