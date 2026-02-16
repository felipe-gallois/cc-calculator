"""Autonomous system entity and utilities."""

from collections.abc import Sequence

MAX_ASN = 2**32 - 1


class ASError(Exception):
    """Any error raised by an AS."""

    pass


class AS:
    """An autonomous system."""

    def __init__(self, asn: int | str) -> None:
        """Initializes an AS object.

        Args:
            asn: The autonomous system number.

        Raises:
            ASError: If asn is invalid.
        """
        try:
            self._asn = int(asn)
        except ValueError as e:
            raise ASError(f"{asn} is not a valid AS number") from e

        if not (0 <= self._asn <= MAX_ASN):
            raise ASError(f"{self._asn} is not a valid AS number")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AS):
            return NotImplemented

        return self._asn == other._asn

    def __hash__(self) -> int:
        return hash(self._asn)

    def __repr__(self) -> str:
        return f"AS({self._asn})"

    def __str__(self) -> str:
        return f"AS{self._asn}"


class ASPath:
    """A path of autonomous systems.

    Attributes:
        path: The sequence of AS that make the path, from first to last.
    """

    def __init__(self, path: Sequence[int | str | AS]) -> None:
        """Initializes an ASPath object.

        Args:
            path: The sequence of ASes.
        """
        self._path = tuple(AS(x) if not isinstance(x, AS) else x for x in path)

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
