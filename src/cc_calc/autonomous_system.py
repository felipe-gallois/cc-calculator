"""Autonomous system."""

_MAX_ASN = 2**32 - 1


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

        if not (0 <= self._asn <= _MAX_ASN):
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
