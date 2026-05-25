from cc_calc.core import AS, ASN, Alpha2Code
from cc_calc.repo._database import ASDB


class ASRepo:
    def __init__(self, as_db: ASDB) -> None:
        self._as_db = as_db
        self._as_dict: dict[ASN, AS] | None = None

    def load_as(self, asn: ASN) -> AS:
        if self._as_dict is None:
            self._as_dict = {
                collected_as.asn: collected_as for collected_as in self._collect_ases()
            }

        return self._as_dict[asn]

    def _collect_ases(self) -> set[AS]:
        return {
            AS(ASN(asn_dto.asn), Alpha2Code(asn_dto.country))
            for asn_dto in self._as_db.load_all_ases()
        }
