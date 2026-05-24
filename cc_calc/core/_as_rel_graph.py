from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from enum import Enum, auto

import networkx as nx

from cc_calc.core._as_path import ASPath
from cc_calc.core._autonomous_system_number import ASN


class RelType(Enum):
    P2C = auto()
    P2P = auto()


@dataclass(frozen=True)
class ASRel:
    src_as: ASN
    dst_as: ASN
    type: RelType


class MissingASError(Exception):
    def __init__(self, asn: ASN) -> None:
        self.asn = asn
        super().__init__(f"AS{asn} is not in the relationships graph")


class PathEstimationError(Exception):
    def __init__(self, src_asn: ASN, dst_asn: ASN) -> None:
        self.src_as = src_asn
        self.dst_as = dst_asn
        super().__init__(f"no paths between AS{src_asn} and AS{dst_asn}")


class ASRelGraph:
    def __init__(self) -> None:
        self._digraph: nx.DiGraph[ASN] = nx.DiGraph()

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

    def add_rel(self, rel: ASRel) -> None:
        self._digraph.add_edge(rel.src_as, rel.dst_as, type=rel.type)

    def get_as_path(self, src_as: ASN, dst_as: ASN) -> ASPath:
        if src_as not in self.nodes:
            raise MissingASError(src_as)

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

        raise PathEstimationError(src_as, dst_as)

    def _get_pred_set(self, asn: ASN) -> set[ASN]:
        try:
            return set(self._digraph.predecessors(asn))
        except nx.NetworkXError as e:
            raise MissingASError(asn) from e

    def _get_succ_set(self, asn: ASN) -> set[ASN]:
        try:
            return set(self._digraph.successors(asn))
        except nx.NetworkXError as e:
            raise MissingASError(asn) from e

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
