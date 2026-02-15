"""Simulation of BGP path propagation."""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from ipaddress import IPv4Network, IPv6Network

MAX_ASN = 2**32 - 1


class ASError(Exception):
    """Any error raised by an AS."""

    pass


class IPPrefixError(Exception):
    """Any error raised by IPv4Prefix or IPv6Prefix."""

    pass


class ASRelGraphError(Exception):
    """Any error raised by an AS relationship graph."""

    pass


class ASRelLoadingError(Exception):
    """Any error raised by an AS relationship loader."""

    pass


class RIBLoadingError(Exception):
    """Any error raised by an RIB loader."""

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
        self._path = [AS(x) if not isinstance(x, AS) else x for x in path]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ASPath):
            return NotImplemented

        return all([True if x == y else False for x, y in zip(self._path, other._path)])

    def __repr__(self) -> str:
        return f"ASPath({self._path})"

    def __str__(self) -> str:
        path_str = [str(x) for x in self._path]
        return f"{'|'.join(path_str)}"


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


class ASRelGraph(ABC):
    """A wrapper for a digraph of autonomous systems and relationship types."""

    @abstractmethod
    def bgp_receivers_from_as(self, curr_as: AS, prev_as: AS | None = None) -> set[AS]:
        """Collects ASes that receive BGP path announcements from an AS.

        The ASes are collected according to the valley-free rule.

        Args:
            curr_as: The AS whose neighbors are being collected.
            prev_as: The AS that announced the path to curr_as (necessary to calculate
                     the valley-free rule).

        Returns: A set of autonomous systems.

        Raises:
            ASRelGraphError: If curr_as is not in the graph.
        """
        pass


class ASRelLoader(ABC):
    """Autonomous system relationship loader."""

    @abstractmethod
    def load_rel_graph(self) -> ASRelGraph:
        """Loads autonomous system relationships.

        Returns:
            An ASRelGraph instance, representing a digraph in which nodes are autonomous
            systems and arcs are relationships. The arcs are annotated with the type of
            the relationship.

        Raises:
            ASRelLoadingException: If there is any problem reading the input file.
        """
        pass


class AdjRIBLoader(ABC):
    """An abstraction for a Adj-RIB-In entry loader."""

    @abstractmethod
    def load_prefix_paths(self) -> dict[IPv4Prefix | IPv6Prefix, list[ASPath]]:
        """Loads Adj-RIB-In entries from a file and maps prefixes to announced paths.

        Returns: A dict, mapping IP prefixes to AS paths that lead to them.

        Raises:
            RIBLoadingError: If the dump file cannot be read.
        """
        pass
