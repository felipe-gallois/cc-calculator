"""CAIDA's AS relationship repository."""

import bz2
from copy import deepcopy
from os import PathLike
from typing import TextIO

from cc_calc.core import (
    ASN,
    ASRel,
    ASRelGraph,
    ASRelGraphRepository,
    ASRelLoadingError,
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
        self._rel_graph: ASRelGraph | None = None

    def load_rel_graph(self) -> ASRelGraph:
        if self._rel_graph is None:
            self._rel_graph = self._get_rel_graph()

        return deepcopy(self._rel_graph)

    def _get_rel_graph(self) -> ASRelGraph:
        try:
            with bz2.open(self._path, mode="rt", encoding="utf-8") as text:
                rel_graph = _build_graph(text)

            return rel_graph
        except Exception as e:
            raise ASRelLoadingError() from e
