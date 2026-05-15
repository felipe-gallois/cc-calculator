from abc import ABC, abstractmethod
from typing import cast

from cc_calc.core._autonomous_system_number import ASN
from cc_calc.core._country_code import CountryCode
from cc_calc.core._ip_prefix import IPPrefix


class IPBlockLoadingError(Exception):
    pass


class IPBlock:
    def __init__(
        self,
        prefix: IPPrefix,
        country: CountryCode | None = None,
        _as: ASN | None = None,
    ) -> None:
        self._prefix = prefix
        self._country = country
        self._as = _as

    def __hash__(self) -> int:
        return hash(self._prefix)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, IPBlock):
            return False

        return self.prefix == other.prefix

    def __len__(self) -> int:
        return cast(int, 2 ** (32 - self._prefix.n_bits))

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


class IPBlockSpecification(ABC):
    @abstractmethod
    def __hash__(self) -> int:
        pass

    @abstractmethod
    def __eq__(self, other: object) -> bool:
        pass

    @abstractmethod
    def is_met_in(self, ip_block: IPBlock) -> bool:
        pass


class IPBlockRepository(ABC):
    @abstractmethod
    def load_blocks_with_specs(self, specs: set[IPBlockSpecification]) -> set[IPBlock]:
        pass
