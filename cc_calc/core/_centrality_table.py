"""Country centrality table."""

import math
from collections import Counter
from collections.abc import ItemsView
from copy import deepcopy
from typing import Self

from cc_calc.core._country_code import CountryCode


class CentralityTable:
    """A country centrality table."""

    def __init__(self, centralities: dict[CountryCode, int] = dict()) -> None:
        self._country_centrality: Counter[CountryCode] = Counter(centralities)
        self._global_centrality = self._country_centrality.total()

    def items(self) -> ItemsView[CountryCode, int]:
        return self._country_centrality.items()

    def add(self, country: CountryCode, points: int) -> None:
        """Adds centrality points to a country.

        Args:
            country: The target country.
            points: The number of points.
        """
        if points == 0:
            return

        self._global_centrality += points
        self._country_centrality[country] += points

    def combine(self, other_table: CentralityTable) -> Self:
        new_table = deepcopy(self)

        other_counter = other_table._country_centrality
        new_table._country_centrality.update(other_counter)
        new_table._global_centrality += other_counter.total()

        return new_table

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
