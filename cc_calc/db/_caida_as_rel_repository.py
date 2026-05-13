"""CAIDA's AS relationship repository."""

import bz2
from os import PathLike
from typing import TextIO

from cc_calc.core import (
    ASN,
    ASRel,
    ASRelGraph,
    ASRelGraphRepository,
    ASRelGraphRepositoryError,
    RelType,
)


def _tokenize(line: str) -> list[str]:
    if "#" in line:
        return []

    splits = line.split("|")
    return splits[0:3] if len(splits) > 2 else []


def _is_p2p(rel_code: str) -> bool:
    return rel_code == "0"


def _build_graph(source: TextIO) -> ASRelGraph:
    rel_graph = ASRelGraph()

    for line in source:
        tokens = _tokenize(line)

        if tokens:
            ases = ASN(tokens[0]), ASN(tokens[1])
            rel_type = tokens[2]

            if _is_p2p(rel_type):
                rel_graph.add_rel(ASRel(ases[0], ases[1], RelType.P2P))
            else:
                rel_graph.add_rel(ASRel(ases[0], ases[1], RelType.P2C))

    return rel_graph


class CaidaASRelRepository(ASRelGraphRepository):
    """Autonomous system relationship loader for the CAIDA AS Relationships Dataset."""

    def __init__(self, path: str | PathLike[str]) -> None:
        """Initializes the loader.

        Args:
            path: A path to the file containing the relationships.
        """
        self._path = path

    def load_rel_graph(self) -> ASRelGraph:
        """Loads autonomous system relationships from CAIDA's dataset.

        Returns: An AS relationship graph.

        Raises:
            ASRelLoadingException: If there is any problem reading the input file.
        """
        try:
            with bz2.open(self._path, mode="rt", encoding="utf-8") as text:
                return _build_graph(text)
        except Exception as e:
            raise ASRelGraphRepositoryError("Could not read input file") from e
