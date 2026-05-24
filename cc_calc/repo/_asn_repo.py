from abc import ABC, abstractmethod
from copy import copy
from typing import Iterator

from cc_calc.core import (
    ASN,
)
from cc_calc.repo._ip_block_repo import ASNDTO


class ASNDB(ABC):
    @abstractmethod
    def load_all_asns(self) -> Iterator[ASNDTO]:
        pass


class ASNRepo:
    def __init__(self, asn_db: ASNDB) -> None:
        self._asn_db = asn_db
        self._asn_set: set[ASN] | None = None

    def load_all_asns(self) -> set[ASN]:
        if self._asn_set is None:
            self._asn_set = self._collect_all_asns()

        return copy(self._asn_set)

    def _collect_all_asns(self) -> set[ASN]:
        return {ASN(asn_dto) for asn_dto in self._asn_db.load_all_asns()}
