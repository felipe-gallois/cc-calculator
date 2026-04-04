"""Autonomous system path."""

from collections.abc import Iterator, Sequence
from typing import overload

from cc_calc.autonomous_system_number import ASN


class ASPathError(Exception):
    """Any error raised by an ASPath."""

    pass


class ASPath:
    """A path of autonomous systems."""

    def __init__(self, path: Sequence[int | str | ASN]) -> None:
        """Initializes an ASPath object.

        Args:
            path: The sequence of ASes.
        """
        self._path = tuple(ASN(x) if not isinstance(x, ASN) else x for x in path)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ASPath):
            return NotImplemented

        if len(self._path) != len(other._path):
            return False

        return all([True if x == y else False for x, y in zip(self._path, other._path)])

    def __hash__(self) -> int:
        return hash(self._path)

    def __repr__(self) -> str:
        return f"ASPath({self._path})"

    def __str__(self) -> str:
        path_str = [str(x) for x in self._path]
        return f"{'|'.join(path_str)}"

    def __len__(self) -> int:
        return len(self._path)

    def __iter__(self) -> Iterator[ASN]:
        for _as in self._path:
            yield _as

    @overload
    def __getitem__(self, key: int) -> ASN:
        pass

    @overload
    def __getitem__(self, key: slice) -> "ASPath":
        pass

    def __getitem__(self, key: int | slice) -> ASN | "ASPath":
        if isinstance(key, slice):
            return ASPath(self._path[key])

        return self._path[key]

    def peek(self) -> ASN | None:
        """Gets the first AS of the AS path.

        Returns: None, if the AS path is empty; otherwise, the first AS on the path.
        """
        if len(self) < 1:
            return None

        return self._path[0]

    def append(self, _as: ASN) -> "ASPath":
        """Appends an AS to the beggining of the AS path.

        Args:
            _as: The autonomous system to append to the path.

        Returns: A new AS path with the appended AS.
        """
        new_sequence = (_as,) + self._path
        return ASPath(new_sequence)

    def pop(self) -> "ASPath":
        """Removes the first AS from the AS path.

        Returns: A new AS path with the first AS removed.

        Raises:
            ASPathError: If attempted to remove an AS from an empty AS path.
        """
        if len(self) < 1:
            raise ASPathError("Tried popping an already empty path")

        new_sequence = self._path[1:]
        return ASPath(new_sequence)
