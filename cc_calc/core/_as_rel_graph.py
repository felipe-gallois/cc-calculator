from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from enum import Enum, auto

import networkx as nx

from cc_calc.core._as_path import ASPath
from cc_calc.core._autonomous_system_number import ASN


class RelType(Enum):
    PROVIDER = auto()
    CLIENT = auto()
    PEER = auto()


@dataclass(frozen=True)
class ASRel:
    src_as: ASN
    dst_as: ASN
    type: RelType


class MissingASError(Exception):
    def __init__(self, asn: ASN) -> None:
        self.asn = asn
        super().__init__(f"AS{asn} is not in the relationships graph")


class ASRelGraph:
    def __init__(self) -> None:
        self._src: ASN | None = None
        self._digraph: nx.DiGraph[ASN] = nx.DiGraph()
        self._paths: dict[ASN, ASPath] = {}

    @property
    def nodes(self) -> set[ASN]:
        return set(self._digraph.nodes)

    @property
    def edges(self) -> set[ASRel]:
        edges = set()

        for src_as, dst_as, attr in self._digraph.edges(data=True):
            rel_type = attr["type"]
            as_rel = ASRel(src_as, dst_as, rel_type)
            edges.add(as_rel)

        return edges

    def clone(self) -> "ASRelGraph":
        clone = ASRelGraph()
        clone._digraph = self._digraph
        return clone

    def add_rel(self, rel: ASRel) -> None:
        if rel.type == RelType.PROVIDER:
            self._digraph.add_edge(rel.src_as, rel.dst_as, type=RelType.PROVIDER)
            self._digraph.add_edge(rel.dst_as, rel.src_as, type=RelType.CLIENT)
        elif rel.type == RelType.CLIENT:
            self._digraph.add_edge(rel.src_as, rel.dst_as, type=RelType.CLIENT)
            self._digraph.add_edge(rel.dst_as, rel.src_as, type=RelType.PROVIDER)
        else:
            self._digraph.add_edge(rel.src_as, rel.dst_as, type=RelType.PEER)
            self._digraph.add_edge(rel.dst_as, rel.src_as, type=RelType.PEER)

    def get_as_path(self, src_as: ASN, dst_as: ASN) -> ASPath:
        if self._src != src_as:
            self._compute_as_paths(src_as)
            self._src = src_as

        return self._search_as_path(dst_as)

    def _search_as_path(self, dst_as: ASN) -> ASPath:
        try:
            return self._paths[dst_as]
        except KeyError as e:
            raise MissingASError(dst_as) from e

    def _compute_as_paths(self, src_as: ASN) -> None:
        self._paths = {src_as: ASPath([src_as])}
        recent = deque([src_as])

        try:
            while len(recent) > 0:
                updated_node = recent.popleft()
                neigh_set = self._get_neigh_set(updated_node)

                for neigh in neigh_set:
                    if (neigh not in self._paths.keys()) and (
                        self._is_valley_free(self._paths[updated_node], neigh)
                    ):
                        self._paths[neigh] = self._paths[updated_node].append(neigh)
                        recent.append(neigh)
        except nx.exception.NetworkXError as e:
            raise MissingASError(src_as) from e

    def _is_valley_free(self, curr_path: ASPath, next_asn: ASN) -> bool:
        try:
            curr_rel = self._digraph[curr_path[-2]][curr_path[-1]]["type"]
            next_rel = self._digraph[curr_path[-1]][next_asn]["type"]

            if (curr_rel in [RelType.PROVIDER, RelType.PEER]) and (
                next_rel != RelType.PROVIDER
            ):
                return False

            return True
        except IndexError:
            return True

    def _get_neigh_set(self, asn: ASN) -> set[ASN]:
        return set(self._digraph.successors(asn))
