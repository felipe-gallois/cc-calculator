from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Iterator

from cc_calc.core import ASN, ASRel, ASRelGraph, RelType


class RelTypeDTO(Enum):
    P2P = auto()
    P2C = auto()


@dataclass
class ASRelDTO:
    src_as: int
    dst_as: int
    rel_type: RelTypeDTO


class ASRelLoadingError(Exception):
    def __init__(self) -> None:
        super().__init__("could not read from AS relationship database")


class ASRelDB(ABC):
    @abstractmethod
    def load_rels(self) -> Iterator[ASRelDTO]:
        pass


class ASRelGraphRepo:
    def __init__(self, as_rel_db: ASRelDB) -> None:
        self._as_rel_db = as_rel_db

    def load_rel_graph(self) -> ASRelGraph:
        graph = ASRelGraph()

        for dto in self._as_rel_db.load_rels():
            src_as = ASN(dto.src_as)
            dst_as = ASN(dto.dst_as)
            rel_type = RelType.P2P if dto.rel_type is RelTypeDTO.P2P else RelType.P2C

            graph.add_rel(ASRel(src_as, dst_as, rel_type))

        return graph
