"""Loading of autonomous systems' relationships."""

import bz2
from os import PathLike
from typing import Iterable, TextIO

import networkx as nx

from cc_calc.as_rel_graph import ASRelGraph, ASRelGraphRepository, _RelType  # FIXME
from cc_calc.autonomous_system import AS


class ASRelLoadingError(Exception):
    """Any error raised by an AS relationship loader."""

    pass


class CaidaRelLoader(ASRelGraphRepository):
    """Autonomous system relationship loader for the CAIDA AS Relationships Dataset."""

    def __init__(self, path: str | PathLike[str]) -> None:
        """Initializes the loader.

        Args:
            path: A path to the file containing the relationships.
        """
        self._path = path

    def load_rel_graph(self) -> ASRelGraph:
        """Loads autonomous system relationships from CAIDA's dataset.

        Returns:
            A NetworkXRelGraph instance, representing a digraph in which nodes are
            autonomous systems and arcs are relationships. The arcs are annotated with
            the type of the relationship.

        Raises:
            ASRelLoadingException: If there is any problem reading the input file.
        """
        try:
            with bz2.open(self._path, mode="rt", encoding="utf-8") as text:
                digraph = self._build_graph(text)
                return ASRelGraph(digraph)
        except Exception as e:
            raise ASRelLoadingError("Could not read input file") from e

    @staticmethod
    def _build_graph(source: TextIO) -> nx.DiGraph[AS]:
        rel_graph = CaidaRelLoader._create_digraph()

        for line in source:
            tokens = CaidaRelLoader._tokenize(line)

            if tokens:
                ases = AS(tokens[0]), AS(tokens[1])
                rel_type = tokens[2]

                CaidaRelLoader._add_nodes(ases, rel_graph)
                CaidaRelLoader._add_edges(ases, rel_graph)

                if CaidaRelLoader._is_p2p(rel_type):
                    CaidaRelLoader._annotate_p2p_edges(ases, rel_graph)
                else:
                    CaidaRelLoader._annotate_p2c_edges(ases, rel_graph)

        return rel_graph

    @staticmethod
    def _create_digraph() -> nx.DiGraph[AS]:
        return nx.DiGraph()

    @staticmethod
    def _tokenize(line: str) -> list[str]:
        if "#" in line:
            return []

        splits = line.split("|")
        return splits[0:3] if len(splits) > 2 else []

    @staticmethod
    def _add_nodes(ases: Iterable[AS], graph: nx.DiGraph[AS]) -> None:
        graph.add_nodes_from(ases)

    @staticmethod
    def _add_edges(ases: tuple[AS, AS], graph: nx.DiGraph[AS]) -> None:
        graph.add_edge(ases[0], ases[1])
        graph.add_edge(ases[1], ases[0])

    @staticmethod
    def _is_p2p(rel_code: str) -> bool:
        return rel_code == "0"

    @staticmethod
    def _annotate_p2p_edges(ases: tuple[AS, AS], graph: nx.DiGraph[AS]) -> None:
        graph.edges[(ases[0], ases[1])]["type"] = _RelType.PEER
        graph.edges[(ases[1], ases[0])]["type"] = _RelType.PEER

    @staticmethod
    def _annotate_p2c_edges(ases: tuple[AS, AS], graph: nx.DiGraph[AS]) -> None:
        graph.edges[(ases[0], ases[1])]["type"] = _RelType.PROVIDER
        graph.edges[(ases[1], ases[0])]["type"] = _RelType.CUSTOMER
