"""Autonomous system relationship graph and utilities."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass
from enum import Enum, auto

import networkx as nx

from cc_calc.core._as_path import ASPath
from cc_calc.core._autonomous_system_number import ASN


class PathEstimationError(Exception):
    pass


class ASRelLoadingError(Exception):
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
        paths: deque[tuple[ASPath, bool]] = deque()

        paths.append((ASPath([dst_as]), True))

        while len(paths) > 0:
            path, went_up = paths.pop()
            first_element = path[0]

            if first_element == src_as:
                return path

            pred_set = self._get_pred_set(first_element)
            succ_set = self._get_succ_set(first_element)
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

        raise PathEstimationError("Failed estimating AS path: no paths between ASes")

    def _get_pred_set(self, asn: ASN) -> set[ASN]:
        try:
            return set(self._digraph.predecessors(asn))
        except nx.NetworkXError as e:
            raise PathEstimationError(
                "Failed estimating AS path: did not expect such ASN"
            ) from e

    def _get_succ_set(self, asn: ASN) -> set[ASN]:
        try:
            return set(self._digraph.successors(asn))
        except nx.NetworkXError as e:
            raise PathEstimationError(
                "Failed estimating AS path: did not expect such ASN"
            ) from e

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
    @abstractmethod
    def load_rel_graph(self) -> ASRelGraph:
        pass
