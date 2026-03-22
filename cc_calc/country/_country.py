"""Country object and utilities."""

from abc import ABC, abstractmethod
from copy import copy

from cc_calc.autonomous_system import ASN
from cc_calc.country._country_code import CountryCode


class CountryRepositoryError(Exception):
    pass


class Country:
    """A country."""

    def __init__(self, code: CountryCode):
        self._code = code
        self._spanned_ases: set[ASN] = set()

    @property
    def code(self) -> CountryCode:
        return self._code

    @property
    def spanned_ases(self) -> set[ASN]:
        return copy(self._spanned_ases)

    def add_as(self, _as: ASN) -> None:
        self._spanned_ases.add(_as)


class CountryRepository(ABC):
    @abstractmethod
    def load_country_with_code(self, code: CountryCode) -> Country:
        pass
