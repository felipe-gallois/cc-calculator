"""Simulation of BGP path propagation."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from ipaddress import ip_network

type AS = str


class ASRelGraphError(Exception):
    """Any error raised by an AS relationship graph."""

    pass


class ASRelLoadingError(Exception):
    """Any error raised by an AS relationship loader."""

    pass


class RIBLoadingError(Exception):
    """Any error raised by an RIB loader."""

    pass


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


class IPPrefix:
    """An IPv4 or IPv6 prefix."""

    def __init__(self, prefix: str) -> None:
        """Initiliazes the prefix.

        Args:
            prefix: A string in prefix format.

        Raises:
            ValueError: If the string is in an invalid format.
        """
        try:
            self._prefix = ip_network(prefix)
        except ValueError as e:
            raise ValueError(f"Tried constructing an IPPrefix with {prefix}") from e

    def __eq__(self, other: object) -> bool:
        """Checks if another object is equal.

        Args:
            other: Another object.

        Returns: True if the object is the same prefix, False otherwise.
        """
        if not isinstance(other, IPPrefix):
            return False

        return self._prefix == other._prefix

    def __hash__(self) -> int:
        """Implements the hash magic method.

        Returns: The hash value for the object.
        """
        return hash(self._prefix)


@dataclass
class RIBEntry:
    """A RIB entry.

    Attributes:
        prefix: The prefix that the path leads to.
        as_path: The sequence of AS that make the path, from first to last.
    """

    prefix: IPPrefix
    as_path: list[AS]


class AdjRIBLoader(ABC):
    """An abstraction for a Adj-RIB-In entry loader."""

    @abstractmethod
    def load_prefix_paths(self) -> dict[IPPrefix, list[list[AS]]]:
        """Loads Adj-RIB-In entries from a file and maps prefixes to announced paths.

        Returns: A dict, mapping IP prefixes to AS paths that lead to them.

        Raises:
            RIBLoadingError: If the dump file cannot be read.
        """
        pass
