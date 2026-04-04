"""Autonomous system."""

from abc import ABC, abstractmethod

from cc_calc.autonomous_system_number import ASN
from cc_calc.country._country_code import CountryCode


class ASRepositoryError(Exception):
    pass


class AS:
    """An autonomous system."""

    def __init__(self, asn: ASN, country_of_registry: CountryCode) -> None:
        self._asn = asn
        self._country_of_registry = country_of_registry

    @property
    def asn(self) -> ASN:
        return self._asn

    @property
    def country_of_registry(self) -> CountryCode:
        return self._country_of_registry


class ASRepository(ABC):
    @abstractmethod
    def load_as(self, asn: ASN) -> AS:
        pass
