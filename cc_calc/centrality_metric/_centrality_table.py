"""Country centrality table."""

import math
from collections import Counter

from cc_calc.country_code import CountryCode


class CentralityTable:
    """A country centrality table."""

    def __init__(self) -> None:
        self._global_centrality = 0
        self._country_centrality: Counter[CountryCode] = Counter()

    def add(self, country: CountryCode, points: int) -> None:
        """Adds centrality points to a country.

        Args:
            country: The target country.
            points: The number of points.
        """
        self._global_centrality += points
        self._country_centrality[country] += points

    def get(self, country: CountryCode) -> int:
        """Retrieves the centrality points of a country.

        Args:
            country: The target country.

        Returns: The number of centrality points of the country.
        """
        return self._country_centrality[country]

    def get_normalized(self, country: CountryCode) -> float:
        """Retrieves the normalized centrality of a country.

        Args:
            country: The target country.

        Returns: The normalized centrality of the country.
        """
        try:
            cc = self._country_centrality[country]
            return cc / self._global_centrality
        except ZeroDivisionError:
            return math.nan
