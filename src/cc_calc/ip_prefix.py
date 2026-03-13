"""IP prefix."""

from ipaddress import IPv4Network, IPv6Network


class IPPrefixError(Exception):
    """Any error raised by IPPrefix."""

    pass


class IPPrefix:
    """An IP prefix."""

    def __init__(self, prefix_str: str) -> None:
        """Initializes an IPPrefix object.

        Args:
            prefix_str: A string corresponding to the IP prefix.

        Raises:
            IPPrefixError: If the string's format is invalid.
        """
        self._prefix: IPv4Network | IPv6Network

        try:
            self._prefix = IPv4Network(prefix_str)
        except Exception:
            try:
                self._prefix = IPv6Network(prefix_str)
            except Exception:
                raise IPPrefixError(f"{str} is not a valid IP prefix")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, IPPrefix):
            return NotImplemented

        return self._prefix == other._prefix

    def __hash__(self) -> int:
        return hash(self._prefix)

    def __repr__(self) -> str:
        return f"IPPrefix('{str(self._prefix)}')"

    def __str__(self) -> str:
        return str(self._prefix)

    @property
    def address_part(self) -> str:
        """The address part of the IP prefix."""
        return str(self._prefix.network_address)
