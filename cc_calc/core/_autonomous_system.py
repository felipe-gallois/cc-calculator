"""Autonomous system."""

from abc import ABC, abstractmethod

from cc_calc.core._autonomous_system_number import ASN
from cc_calc.core._country_code import CountryCode


class ASLoadingError(Exception):
    pass


class AS:
    """An autonomous system."""

    def __init__(
        self, asn: ASN, country_of_registry: CountryCode | None = None
    ) -> None:
        self._asn = asn
        self._country_of_registry = country_of_registry

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AS):
            return False

        if self._asn != other._asn:
            return False

        return True

    def __hash__(self) -> int:
        return hash(self._asn)

    @property
    def asn(self) -> ASN:
        return self._asn

    @property
    def country_of_registry(self) -> CountryCode | None:
        return self._country_of_registry

    @country_of_registry.setter
    def country_of_registry(self, country: CountryCode) -> None:
        self._country_of_registry = country


class ASRepository(ABC):
    @abstractmethod
    def load_as(self, asn: ASN) -> AS:
        pass
