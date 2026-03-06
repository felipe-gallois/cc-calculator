"""Country object and utilities."""

from collections.abc import Iterator, Sequence
from itertools import chain
from typing import overload


class CountryError(Exception):
    """Any error raised by a Country."""

    pass


class Country:
    """A country."""

    def __init__(self, code: str):
        """Initializes the Country object.

        Args:
            code: The alpha-2 code that represents the country.

        Raises:
            CountryError: If code is not in alpha-2 format.
        """
        if len(code) != 2 or (not code.isalpha()):
            raise CountryError(f"{code} is an invalid alpha-2 country code")

        self._alpha2 = code.upper()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Country):
            return False

        return self._alpha2 == other._alpha2

    def __hash__(self) -> int:
        return hash(self._alpha2)

    def __repr__(self) -> str:
        return f"Country('{self._alpha2}')"

    def __str__(self) -> str:
        return self._alpha2


class CountryPath:
    """A country path.

    A country path is a sequence of countries in which the same countries do not appear
    twice in a row. For example, CA->US->BR would be a valid path, whereas US->US would
    not.
    """

    def __init__(self, seq: Sequence[Country]) -> None:
        """Initializes a CountryPath.

        Args:
            seq: A sequence of countries from which to build the path.
        """
        self._path = tuple(
            chain(seq[0:1], [curr for prev, curr in zip(seq, seq[1:]) if curr != prev])
        )

    def __len__(self) -> int:
        return len(self._path)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CountryPath):
            return False

        return self._path == other._path

    def __hash__(self) -> int:
        return hash(self._path)

    def __repr__(self) -> str:
        country_repr_list = [repr(country) for country in self._path]
        return f"CountryPath([{', '.join(country_repr_list)}])"

    def __iter__(self) -> Iterator[Country]:
        for country in self._path:
            yield country

    @overload
    def __getitem__(self, key: int) -> Country | None:
        pass

    @overload
    def __getitem__(self, key: slice) -> "CountryPath":
        pass

    def __getitem__(self, key: int | slice) -> Country | "CountryPath" | None:
        if isinstance(key, slice):
            return CountryPath(self._path[key])

        try:
            return self._path[key]
        except IndexError:
            return None
