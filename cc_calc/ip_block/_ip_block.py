from abc import ABC, abstractmethod

from cc_calc.autonomous_system_number import ASN
from cc_calc.country_code import CountryCode
from cc_calc.ip_prefix import IPPrefix


class IPBlockRepositoryError(Exception):
    pass


class IPBlock:
    def __init__(self, prefix: IPPrefix) -> None:
        self._prefix = prefix
        self._country: CountryCode | None = None
        self._as: ASN | None = None

    def __hash__(self) -> int:
        return hash(self._prefix)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, IPBlock):
            return False

        return self.prefix == other.prefix

    @property
    def prefix(self) -> IPPrefix:
        return self._prefix

    @property
    def country(self) -> CountryCode | None:
        return self._country

    @country.setter
    def country(self, code: CountryCode | None) -> None:
        self._country = code

    @property
    def autonomous_system(self) -> ASN | None:
        return self._as

    @autonomous_system.setter
    def autonomous_system(self, asn: ASN | None) -> None:
        self._as = asn


class IPBlockRepository(ABC):
    @abstractmethod
    def load_blocks_in_country(self, country: CountryCode) -> set[IPBlock]:
        pass
