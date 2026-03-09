"""Country centrality."""

from collections import Counter

from cc_calc.country import Country


class CountryCentrality:
    """Maps countries to centrality values."""

    def __init__(self) -> None:
        self._cc: Counter[Country] = Counter()

    def __getitem__(self, country: str | Country) -> int:
        return self.get(country)

    def get(self, country: str | Country) -> int:
        """Retrieves the centrality value of a country.

        Args:
            country: The target country.

        Returns: The current centrality of a country.
        """
        if isinstance(country, str):
            country = Country(country)

        return self._cc[country]

    def add(self, country: str | Country, points: int) -> None:
        """Adds centrality points to a country.

        Args:
            country: The target country.
            points: The number of points to add.
        """
        if isinstance(country, str):
            country = Country(country)

        self._cc[country] += points
