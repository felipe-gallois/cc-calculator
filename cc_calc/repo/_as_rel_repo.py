from cc_calc.core import ASN, ASRel, ASRelGraph, RelType
from cc_calc.repo._database import ASRelDB
from cc_calc.repo._dto import RelTypeDTO


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
