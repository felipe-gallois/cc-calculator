from dataclasses import dataclass
from enum import Enum, auto

type ASNDTO = int
type CountryDTO = str
type IPPrefixDTO = str


@dataclass
class ASDTO:
    asn: ASNDTO
    country: CountryDTO


class RelTypeDTO(Enum):
    P2P = auto()
    P2C = auto()


@dataclass
class ASRelDTO:
    src_as: int
    dst_as: int
    rel_type: RelTypeDTO
