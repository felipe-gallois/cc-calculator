from collections.abc import Iterator, Sequence
from itertools import chain
from typing import overload


class CountryError(Exception):
    pass


class Country:
    def __init__(self, code: str):
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
    def __init__(self, path: Sequence[Country]) -> None:
        self._path = list(
            chain(
                path[0:1], [curr for prev, curr in zip(path, path[1:]) if curr != prev]
            )
        )

    def __len__(self) -> int:
        return len(self._path)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CountryPath):
            return False

        return self._path == other._path

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
