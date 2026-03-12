"""Autonomous system relationship graph and utilities."""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any

import networkx as nx

from cc_calc.autonomous_system import AS


class ASRelGraphError(Exception):
    """Any error raised by an AS relationship graph."""

    pass


class _RelType(Enum):
    CUSTOMER = auto()
    PROVIDER = auto()
    PEER = auto()


class ASRelGraph:
    """A digraph of autonomous systems and relationship types."""

    def __init__(self, digraph: nx.DiGraph[AS]) -> None:
        """Initializes the digraph.

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

        if self._as_rel(prev_as, curr_as) == _RelType.CUSTOMER:
            return succ

        return {s for s in succ if self._as_rel(curr_as, s) == _RelType.PROVIDER}

    def _successors(self, as_: AS) -> set[AS]:
        try:
            return set(self._digraph.successors(as_))
        except nx.NetworkXError as e:
            raise ASRelGraphError(f"{as_} is not in the graph") from e

    def _as_rel(self, src_as: AS, dst_as: AS) -> Any:
        return self._digraph.edges[(src_as, dst_as)]["type"]


class ASRelGraphRepository(ABC):
    """Autonomous system relationship loader."""

    @abstractmethod
    def load_rel_graph(self) -> ASRelGraph:
        """Loads autonomous system relationships.

        Returns:
            An ASRelGraph instance, representing a digraph in which nodes are autonomous
            systems and arcs are relationships. The arcs are annotated with the type of
            the relationship.

        Raises:
            ASRelLoadingException: If there is any problem reading the input file.
        """
        pass
