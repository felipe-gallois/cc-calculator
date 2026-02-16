"""IP prefix entities and utilities."""

from ipaddress import IPv4Network, IPv6Network


class IPPrefixError(Exception):
    """Any error raised by IPv4Prefix or IPv6Prefix."""

    pass


class IPv4Prefix:
    """An IPv4 prefix."""

    def __init__(self, prefix_str: str) -> None:
        """Initializes an IPv4Prefix object.

        Args:
            prefix_str: A string corresponding to the IPv4 prefix.

        Raises:
            IPPrefixError: If the string's format is invalid.
        """
        try:
            self._prefix = IPv4Network(prefix_str)
        except Exception as e:
            raise IPPrefixError(f"{prefix_str} is not a valid IPv4 prefix") from e

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, IPv4Prefix):
            return NotImplemented

        return self._prefix == other._prefix

    def __hash__(self) -> int:
        return hash(self._prefix)

    def __repr__(self) -> str:
        return f"IPv4Prefix('{str(self._prefix)}')"

    def __str__(self) -> str:
        return str(self._prefix)


class IPv6Prefix:
    """An IPv6 prefix."""

    def __init__(self, prefix_str: str) -> None:
        """Initializes an IPv6Prefix object.

        Args:
            prefix_str: A string corresponding to the IPv6 prefix.

        Raises:
            IPPrefixError: If the string's format is invalid.
        """
        try:
            self._prefix = IPv6Network(prefix_str)
        except Exception as e:
            raise IPPrefixError(f"{prefix_str} is not a valid IPv6 prefix") from e

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, IPv6Prefix):
            return NotImplemented

        return self._prefix == other._prefix

    def __hash__(self) -> int:
        return hash(self._prefix)

    def __repr__(self) -> str:
        return f"IPv6Prefix('{str(self._prefix)}')"

    def __str__(self) -> str:
        return str(self._prefix)


def ip_prefix(prefix: str) -> IPv4Prefix | IPv6Prefix:
    """Creates an IPv4Prefix or IPv6Prefix object from a prefix string.

    Args:
        prefix: The prefix string.

    Returns: An IPv4Prefix or IPv6Prefix object.

    Raises:
        IPPrefixError: If neither an IPv4Prefix, nor an IPv6Prefix object could be
        created.
    """
    try:
        return IPv4Prefix(prefix)
    except Exception:
        try:
            return IPv6Prefix(prefix)
        except Exception:
            raise IPPrefixError(f"{str} is not a valid IPv4 or IPv6 prefix")
