"""ASCountryMap and utilities."""

from abc import ABC, abstractmethod

from cc_calc.autonomous_system import AS
from cc_calc.country import CountryCode


class ASCountryMapRepositoryError(Exception):
    """Any error raised by an AS-to-country map repository."""

    pass


class ASCountryMap:
    """A map connecting autonomous systems to countries."""

    def __init__(self, map: dict[AS, CountryCode]):
        """Initializes the map.

        Args:
            map: A dict mapping ASes to countries.
        """
        self._map = map

    def __getitem__(self, key: AS) -> CountryCode:
        return self._map[key]


class ASCountryMapRepository(ABC):
    """An AS-to-country map repository."""

    @abstractmethod
    def load_as_country_map(self) -> ASCountryMap:
        """Loads the AS-to-country map from the repository.

        Returns: The map.

        Raises:
            ASCountryMapRepositoryError: If the map cannot be loaded.
        """
        pass
