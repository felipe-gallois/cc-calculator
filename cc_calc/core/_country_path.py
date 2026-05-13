"""Country path and utilities."""

from abc import ABC
from collections.abc import Iterator, Sequence
from copy import copy
from dataclasses import dataclass
from itertools import chain
from typing import overload

from cc_calc.core._country_code import CountryCode


@dataclass
class CountryPathEvent(ABC):
    """Generic country path event."""

    pass


@dataclass
class UnknownCountryEvent(CountryPathEvent):
    """When at least one of the countries of the country sequence is unknown (None)."""

    pass


class CountryPath:
    """A country path.

    A country path is a sequence of countries in which the same countries do not appear
    twice in a row. For example, CA->US->BR would be a valid path, whereas US->US would
    not.
    """

    def __init__(self, seq: Sequence[CountryCode | None]) -> None:
        """Initializes a CountryPath.

        Args:
            seq: A sequence of countries from which to build the path. None is a valid
            sequence element, and represents an unknown country.
        """
        self._path: tuple[CountryCode, ...]

        match len(seq):
            case 0:
                self._path = ()
            case 1:
                self._path = () if seq[0] is None else (seq[0],)
            case _:
                country_seq: list[CountryCode] = [
                    country for country in seq if country is not None
                ]

                self._path = tuple(
                    chain(
                        country_seq[:1],
                        [
                            curr
                            for prev, curr in zip(country_seq, country_seq[1:])
                            if curr != prev
                        ],
                    )
                )

        self._events: list[CountryPathEvent] = []

        if None in seq:
            self._events.append(UnknownCountryEvent())

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
        return f"CountryPath(({', '.join(country_repr_list)}))"

    def __iter__(self) -> Iterator[CountryCode]:
        for country in self._path:
            yield country

    @overload
    def __getitem__(self, key: int) -> CountryCode | None:
        pass

    @overload
    def __getitem__(self, key: slice) -> "CountryPath":
        pass

    def __getitem__(self, key: int | slice) -> CountryCode | "CountryPath" | None:
        if isinstance(key, slice):
            return CountryPath(self._path[key])

        try:
            return self._path[key]
        except IndexError:
            return None

    @property
    def events(self) -> list[CountryPathEvent]:
        """The events collected by this object."""
        return copy(self._events)

    @property
    def countries(self) -> set[CountryCode]:
        return {country for country in self._path}

    def clear_events(self) -> None:
        """Clears the event list of this object."""
        self._events.clear()
