"""ASCountryMap and utilities."""

from cc_calc.autonomous_system import AS
from cc_calc.country import Country


class ASCountryMap:
    """A map connecting autonomous systems to countries."""

    def __init__(self, map: dict[AS, Country]):
        """Initializes the map.

        Args:
            map: A dict mapping ASes to countries.
        """
        self._map = map
