"""Autonomous system relationship graph and utilities."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass
from enum import Enum, auto

import networkx as nx

from cc_calc.as_path_estimation._as_path import ASPath
from cc_calc.autonomous_system_number import ASN


class ASRelGraphError(Exception):
    """Any error raised by an AS relationship graph."""

    pass


class ASRelGraphRepositoryError(Exception):
    """Any error raised by an AS relationship graph repository."""

    pass


class RelType(Enum):
    """The type of AS relationship."""

    P2C = auto()
    P2P = auto()


@dataclass(frozen=True)
class ASRel:
    """An AS relationship.

    Relationships are implicitly considered reciprocal. Every provider-to-client
    relationship entails a client-to-provider counterpart. Likewise, a peer-to-peer
    relationship goes both ways.

    Attributes:
        src_as: The source AS.
        dst_as: The destination AS.
        type: The relationship type.
    """

    src_as: ASN
    dst_as: ASN
    type: RelType


class ASRelGraph:
    """A digraph of autonomous systems and relationship types."""

    def __init__(self) -> None:
        """Initializes the digraph.

        Args:
            digraph: The internal digraph.
        """
        self._digraph: nx.DiGraph[ASN] = nx.DiGraph()

    @property
    def nodes(self) -> set[ASN]:
        """The nodes of the graph."""
        return set(self._digraph.nodes)

    @property
    def edges(self) -> set[ASRel]:
        """The edges (relationships) of the graph."""
        edges = set()

        for src_as, dst_as, attr in self._digraph.edges(data=True):
            rel_type = attr["type"]
            as_rel = ASRel(src_as, dst_as, rel_type)
            edges.add(as_rel)

        return edges

    def add_rel(self, rel: ASRel) -> None:
        """Adds a relationship to the graph.

        Args:
            rel: The relationship.
        """
        self._digraph.add_edge(rel.src_as, rel.dst_as, type=rel.type)

    def get_as_path(self, src_as: ASN, dst_as: ASN) -> ASPath:
        """Calculates the shortest AS path between two ASes.

        This method calculates the shortest AS path between two ASes that follows the
        valley-free principle. This principle describes what data paths between ASes
        can be expected in normal circunstances, given real-world economic
        relationships between Internet service providers.

        Args:
            src_as: The source AS.
            dst_as: The destination AS.

        Returns: The calculated AS path.

        Raises:
            ASRelGraphError: If the source or the destination ASes are not in the graph,
            or no path exists between ASes.
        """
        if src_as not in self.nodes:
            raise ASRelGraphError(
                f"Cannot calculate path from {src_as} because it is not in the graph"
            )

        if dst_as not in self.nodes:
            raise ASRelGraphError(
                f"Cannot calculate path to {dst_as} because it is not in the graph"
            )

        paths: deque[tuple[ASPath, bool]] = deque()
        paths.append((ASPath([dst_as]), True))

        while len(paths) > 0:
            path, went_up = paths.pop()
            first_element = path[0]

            if first_element == src_as:
                return path

            pred_set = set(self._digraph.predecessors(first_element))
            succ_set = set(self._digraph.successors(first_element))
            neigh_set = pred_set | succ_set

            for neigh in neigh_set:
                if neigh in path:
                    continue

                if (not went_up) and (not self._is_provider(first_element, neigh)):
                    continue

                appended_path = (
                    (path.append(neigh), True)
                    if self._is_customer(first_element, neigh)
                    else (path.append(neigh), False)
                )

                paths.append(appended_path)

        raise ASRelGraphError(f"Did not find path between {src_as} and {dst_as}")

    def _is_provider(self, src_as: ASN, dst_as: ASN) -> bool:
        provider = False

        try:
            rel_type = self._digraph.edges[(src_as, dst_as)]["type"]

            if rel_type == RelType.P2C:
                provider = True
        except KeyError:
            pass

        return provider

    def _is_customer(self, src_as: ASN, dst_as: ASN) -> bool:
        customer = False

        try:
            rel_type = self._digraph.edges[(dst_as, src_as)]["type"]

            if rel_type == RelType.P2C:
                customer = True
        except KeyError:
            pass

        return customer


class ASRelGraphRepository(ABC):
    """AS relationship graph repository."""

    @abstractmethod
    def load_rel_graph(self) -> ASRelGraph:
        """Loads the AS relationship graph.

        Returns: The relationship graph.

        Raises:
            ASRelLoadingException: If there is any problem reading the input file.
        """
        pass
