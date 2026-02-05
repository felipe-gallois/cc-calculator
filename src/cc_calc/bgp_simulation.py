"""Simulation of BGP path propagation."""

from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass
from ipaddress import IPv4Network, IPv6Network

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


class RIBLoader(ABC):
    @abstractmethod
    def iter(self) -> Iterator[RIBEntry]:
        pass


@dataclass
class RIBEntry:
    prefix: IPv4Network | IPv6Network
    as_path: list[AS]
