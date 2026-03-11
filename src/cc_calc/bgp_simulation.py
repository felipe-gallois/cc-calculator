"""Simulation of BGP path propagation."""

from abc import ABC, abstractmethod
from collections import deque
from collections.abc import Iterable

from cc_calc.as_path import ASPath
from cc_calc.autonomous_system import AS
from cc_calc.loc_rib import LocRIBManagerError, SimpleLocRIBManager
from cc_calc.prefix_sure_as_path_list import PrefixSureASPathList


class ASRelGraphError(Exception):
    """Any error raised by an AS relationship graph."""

    pass


class ASRelLoadingError(Exception):
    """Any error raised by an AS relationship loader."""

    pass


class ASPathEstimationError(Exception):
    """Any error raised by an AS path estimator."""

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


def _collect_base_as_set(known_paths: Iterable[ASPath]) -> set[AS]:
    return {_as for path in known_paths for _as in path}


class SimpleASPathEstimator:
    """A simple implementation of an AS path estimator."""

    def __init__(self) -> None:
        """Initializes the object."""
        self._rib_manager = SimpleLocRIBManager()

    def fit(
        self,
        as_rel_graph: ASRelGraph,
        sure_paths: PrefixSureASPathList,
    ) -> None:
        """Fits the estimator to the provided data.

        The estimator calculates the AS paths from every AS to some prefix.

        Args:
            as_rel_graph: An AS relationship graph.
            sure_paths: A list of sure AS paths to a prefix.
        """
        update_queue: deque[AS] = deque()

        self._insert_sure_paths(sure_paths)

        for _as in _collect_base_as_set(sure_paths):
            update_queue.append(_as)

        while len(update_queue) != 0:
            updated_as = update_queue.popleft()
            as_path = self._rib_manager.best_path(updated_as)

            appended_path = as_path.append(updated_as)

            prev_as = as_path[0]

            peers = as_rel_graph.bgp_receivers_from_as(updated_as, prev_as)

            for peer in peers:
                self._rib_manager.eval_unsure_path(peer, appended_path)

                if self._rib_manager.performed_unsure_update:
                    update_queue.append(peer)

    def predict(self, src_as: AS) -> ASPath:
        """Predicts the AS path to the fitted prefix, from the provided AS.

        Args:
            src_as: The source autonomous system.

        Returns: The predicted AS path.

        Raises:
            ASPathEstimationError: If no path to the prefix is predicted from the AS.
        """
        try:
            return self._rib_manager.best_path(src_as)
        except LocRIBManagerError as e:
            raise ASPathEstimationError(f"{src_as} was not fitted") from e

    def _insert_sure_paths(self, sure_paths: Iterable[ASPath]) -> None:
        for path in sure_paths:
            self._rib_manager.eval_sure_path_recursively(path)
