"""Loading of autonomous systems' relationships."""

import bz2
from os import PathLike
from typing import Any, Iterable, TextIO

import networkx as nx

from cc_calc.autonomous_system import AS
from cc_calc.bgp_simulation import (
    ASRelGraph,
    ASRelGraphError,
    ASRelLoader,
    ASRelLoadingError,
)


class NetworkXRelGraph(ASRelGraph):
    """A wrapper for a NetworkX digraph of autonomous systems and relationship types."""

    def __init__(self, digraph: nx.DiGraph[AS]) -> None:
        """Initializes the wrapper.

        Args:
            digraph: The internal digraph.
        """
        self._digraph = digraph

    def bgp_receivers_from_as(
        self, curr_as: int | str | AS, prev_as: int | str | AS | None = None
    ) -> set[AS]:
        """Collects ASes that receive BGP path announcements from an AS.

        The ASes are collected according to the valley-free rule.

        Args:
            curr_as: The AS whose neighbors are being collected.
            prev_as: The AS that announced the path to curr_as (necessary to calculate
                     the valley-free rule).

        Returns: A set of autonomous systems.

        Raises:
            ASRelGraphError: If curr_as is not in the graph.
        """
        if not isinstance(curr_as, AS):
            curr_as = AS(curr_as)

        succ = self._successors(curr_as)

        if not prev_as:
            return succ

        if not isinstance(prev_as, AS):
            prev_as = AS(prev_as)

        if self._as_rel(prev_as, curr_as) == "customer":
            return succ

        return {s for s in succ if self._as_rel(curr_as, s) == "customer"}

    def _successors(self, as_: AS) -> set[AS]:
        try:
            return set(self._digraph.successors(as_))
        except nx.NetworkXError as e:
            raise ASRelGraphError(f"{as_} is not in the graph") from e

    def _as_rel(self, src_as: AS, dst_as: AS) -> Any:
        return self._digraph.edges[(src_as, dst_as)]["type"]


class CaidaRelLoader(ASRelLoader):
    """Autonomous system relationship loader for the CAIDA AS Relationships Dataset."""

    def __init__(self, path: str | PathLike[str]) -> None:
        """Initializes the loader.

        Args:
            path: A path to the file containing the relationships.
        """
        self._path = path

    def load_rel_graph(self) -> NetworkXRelGraph:
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
                return NetworkXRelGraph(digraph)
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
        graph.edges[(ases[0], ases[1])]["type"] = "peer"
        graph.edges[(ases[1], ases[0])]["type"] = "peer"

    @staticmethod
    def _annotate_p2c_edges(ases: tuple[AS, AS], graph: nx.DiGraph[AS]) -> None:
        graph.edges[(ases[0], ases[1])]["type"] = "provider"
        graph.edges[(ases[1], ases[0])]["type"] = "custumer"
