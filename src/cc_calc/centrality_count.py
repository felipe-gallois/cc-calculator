"""Country centrality counting."""

import math
from collections import Counter

from cc_calc.country import Country


def _norm_country(country: str | Country) -> Country:
    if isinstance(country, str):
        country = Country(country)

    return country


class CentralityCounter:
    """A country centrality counter."""

    def __init__(self) -> None:
        self._global_centrality = 0
        self._country_centrality: Counter[Country] = Counter()

    def add(self, country: str | Country, points: int) -> None:
        """Adds centrality points to a country.

        Args:
            country: The target country.
            points: The number of points.
        """
        country = _norm_country(country)
        self._global_centrality += points
        self._country_centrality[country] += points

    def get(self, country: str | Country) -> int:
        """Retrieves the centrality points of a country.

        Args:
            country: The target country.

        Returns: The number of centrality points of the country.
        """
        country = _norm_country(country)
        return self._country_centrality[country]

    def get_normalized(self, country: str | Country) -> float:
        """Retrieves the normalized centrality of a country.

        Args:
            country: The target country.

        Returns: The normalized centrality of the country.
        """
        try:
            country = _norm_country(country)
            cc = self._country_centrality[country]
            return cc / self._global_centrality
        except ZeroDivisionError:
            return math.nan
