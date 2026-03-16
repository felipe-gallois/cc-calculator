"""Autonomous system relationship graph and utilities."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto

import networkx as nx

from cc_calc.autonomous_system import AS


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

    src_as: AS
    dst_as: AS
    type: RelType


class ASRelGraph:
    """A digraph of autonomous systems and relationship types."""

    def __init__(self) -> None:
        """Initializes the digraph.

        Args:
            digraph: The internal digraph.
        """
        self._digraph: nx.DiGraph[AS] = nx.DiGraph()

    @property
    def nodes(self) -> set[AS]:
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

        succ = self._neighbors(curr_as)

        if not prev_as:
            return succ

        if not isinstance(prev_as, AS):
            prev_as = AS(prev_as)

        succ.discard(prev_as)

        if self._is_customer(prev_as, curr_as):
            return succ

        return {s for s in succ if self._is_provider(curr_as, s)}

    def _neighbors(self, as_: AS) -> set[AS]:
        try:
            return set(self._digraph.neighbors(as_))
        except nx.NetworkXError as e:
            raise ASRelGraphError(f"{as_} is not in the graph") from e

    def _is_provider(self, src_as: AS, dst_as: AS) -> bool:
        provider = False

        try:
            rel_type = self._digraph.edges[(src_as, dst_as)]["type"]

            if rel_type == RelType.P2C:
                provider = True
        except KeyError:
            pass

        return provider

    def _is_customer(self, src_as: AS, dst_as: AS) -> bool:
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
