from abc import ABC, abstractmethod
from typing import Iterator

from cc_calc.repo._dto import ASDTO, ASNDTO, ASRelDTO, CountryDTO, IPPrefixDTO


class UnreachableDB(Exception):
    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(f"could not reach {name}")


class InvalidDBDataFormat(Exception):
    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(f"unexpected data format in {name}")


class ASNDB(ABC):
    @abstractmethod
    def load_all_asns(self) -> Iterator[ASNDTO]:
        pass


class ASDB(ABC):
    @abstractmethod
    def load_all_ases(self) -> Iterator[ASDTO]:
        pass


class ASRelDB(ABC):
    @abstractmethod
    def load_rels(self) -> Iterator[ASRelDTO]:
        pass


class PrefixASNDB(ABC):
    @abstractmethod
    def load_prefix_asn(self, prefix: IPPrefixDTO) -> ASNDTO | None:
        pass


class PrefixCountryDB(ABC):
    @abstractmethod
    def load_prefix_country(self, prefix: IPPrefixDTO) -> CountryDTO | None:
        pass


class IPPrefixDB(ABC):
    @abstractmethod
    def load_all_ip_prefixes(self) -> Iterator[IPPrefixDTO]:
        pass
