import math
from collections import Counter
from collections.abc import ItemsView
from copy import deepcopy
from typing import Self

from cc_calc.core._country_code import Alpha2Code, CountryCode


class CentralityTable:
    def __init__(self, centralities: dict[CountryCode, int] = dict()) -> None:
        self._country_centrality: Counter[CountryCode] = Counter(centralities)
        self._excused_centrality: Counter[CountryCode] = Counter()
        self._global_centrality = self._country_centrality.total()

    def items(self) -> ItemsView[CountryCode, int]:
        return self._country_centrality.items()

    def add(self, country: CountryCode, points: int) -> None:
        if points == 0:
            return

        self._country_centrality[country] += points

    def add_global(self, points: int) -> None:
        self._global_centrality += points

    def add_excused(self, country: CountryCode, points: int) -> None:
        self._excused_centrality[country] += points

    def combine(self, other_table: CentralityTable) -> Self:
        new_table = deepcopy(self)

        other_cc = other_table._country_centrality
        new_table._country_centrality.update(other_cc)

        other_excused = other_table._excused_centrality
        new_table._excused_centrality.update(other_excused)

        new_table._global_centrality += other_cc.total()

        return new_table

    def get(self, country: CountryCode) -> int:
        return self._country_centrality[country]

    def get_global(self) -> int:
        return self._global_centrality

    def get_excused(self, country: CountryCode) -> int:
        return self._excused_centrality[country]

    def get_normalized(self, country: CountryCode) -> float:
        try:
            cc = self._country_centrality[country]
            excused = self._excused_centrality[country]
            return cc / (self._global_centrality - excused)
        except ZeroDivisionError:
            return math.nan
