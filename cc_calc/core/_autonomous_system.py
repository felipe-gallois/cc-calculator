"""Autonomous system."""

from abc import ABC, abstractmethod

from cc_calc.core._autonomous_system_number import ASN
from cc_calc.core._country_code import CountryCode


class ASRepositoryError(Exception):
    pass


class AS:
    """An autonomous system."""

    def __init__(
        self, asn: ASN, country_of_registry: CountryCode | None = None
    ) -> None:
        self._asn = asn
        self._country_of_registry = country_of_registry

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
