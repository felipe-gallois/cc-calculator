import bz2
from os import PathLike
from typing import Protocol, TextIO

import networkx as nx


class ASRelLoader(Protocol):
    def load_rel_graph(self) -> nx.DiGraph[str]: ...


class CaidaRelLoader:
    def __init__(self, path: str | PathLike[str]) -> None:
        self._path = path

    def load_rel_graph(self) -> nx.DiGraph[str]:
        with bz2.open(self._path, mode="rt", encoding="utf-8") as text:
            return self._build_graph(text)

    @staticmethod
    def _build_graph(source: TextIO) -> nx.DiGraph[str]:
        rel_graph = CaidaRelLoader._create_digraph()

        for line in source:
            tokens = CaidaRelLoader._tokenize(line)

            if tokens:
                asns = tokens[0:2]
                rel_type = tokens[2]

                CaidaRelLoader._add_nodes(asns, rel_graph)
                CaidaRelLoader._add_edges(asns, rel_graph)

                if CaidaRelLoader._is_p2p(rel_type):
                    CaidaRelLoader._annotate_p2p_edges(asns, rel_graph)
                else:
                    CaidaRelLoader._annotate_p2c_edges(asns, rel_graph)

        return rel_graph

    @staticmethod
    def _create_digraph() -> nx.DiGraph[str]:
        return nx.DiGraph()

    @staticmethod
    def _tokenize(line: str) -> list[str]:
        if "#" in line:
            return []

        splits = line.split("|")
        return splits[0:3] if len(splits) > 2 else []

    @staticmethod
    def _add_nodes(asns: list[str], graph: nx.DiGraph[str]) -> None:
        graph.add_nodes_from(asns)

    @staticmethod
    def _add_edges(asns: list[str], graph: nx.DiGraph[str]) -> None:
        graph.add_edge(asns[0], asns[1])
        graph.add_edge(asns[1], asns[0])

    @staticmethod
    def _is_p2p(rel_code: str) -> bool:
        return rel_code == "0"

    @staticmethod
    def _annotate_p2p_edges(asns: list[str], graph: nx.DiGraph[str]) -> None:
        graph.edges[(asns[0], asns[1])]["type"] = "peer"
        graph.edges[(asns[1], asns[0])]["type"] = "peer"

    @staticmethod
    def _annotate_p2c_edges(asns: list[str], graph: nx.DiGraph[str]) -> None:
        graph.edges[(asns[0], asns[1])]["type"] = "provider"
        graph.edges[(asns[1], asns[0])]["type"] = "custumer"
