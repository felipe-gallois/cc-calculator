"""Simplified Loc-RIB model."""

from abc import ABC
from copy import copy
from dataclasses import dataclass

from cc_calc.as_path_estimation._as_path import ASPath
from cc_calc.as_path_estimation._autonomous_system import AS
from cc_calc.ip_prefix import IPPrefix


class LocRIBModelError(Exception):
    """Any error raised by a Loc-RIB manager."""

    pass


@dataclass(frozen=True)
class LocRIBModelEvent(ABC):
    """Generic Loc-RIB model event."""

    pass


@dataclass(frozen=True)
class SecondSurePathEvent(LocRIBModelEvent):
    """Event for when the client wants to overwrite an installed sure path."""

    target: AS
    old_path: ASPath
    new_path: ASPath


class LocRIBModel:
    """A simplified Loc-RIB model for a single IP prefix.

    This class manages predicted Loc-RIB tables for different ASes (it simplifies the
    problem, assuming only one router per AS).

    It evaluates paths to IP prefixes announced by Adj-RIB-In tables, keeping only the
    best one for each AS, according to some simple heuristics, and considering that some
    Adj-RIB-In entries are sure, while others are infered. The heuristics for selecting
    the best path are summarized as follows: the shorter paths are chosen over longer
    ones, but the sure paths are always given preference over unsure ones.
    """

    def __init__(self, prefix: IPPrefix) -> None:
        """Initializes the object.

        Args:
            prefix: The destination prefix for the stored AS paths.
        """
        self._prefix = IPPrefix

        self._events: list[LocRIBModelEvent] = []

        self._loc_ribs: dict[AS, ASPath] = dict()
        self._sure_paths: dict[AS, bool] = dict()

    @property
    def events(self) -> list[LocRIBModelEvent]:
        """The list of events produced by the object."""
        return copy(self._events)

    def clear_events(self) -> None:
        """Clears the object's events."""
        self._events.clear()

    def add_path(self, src_as: AS, path: ASPath, sureness: bool = False) -> bool:
        """Adds a path to the Loc-RIB model.

        Args:
            src_as: The AS that receives the Adj-RIB-In path.
            path: The AS path to the prefix.
            sureness: A boolean indicating whether the path is sure or not.

        Returns: A boolean, telling if the operation caused a best path update.
        """
        updated = False

        try:
            rib_path = self._loc_ribs[src_as]
            rib_sure = self._sure_paths[src_as]

            if rib_sure and sureness is True:
                self._generate_second_sure_path_event(src_as, rib_path, path)

            if (not rib_sure) and (len(rib_path) > len(path)):
                self._update_loc_rib(src_as, path, False)
                updated = True
        except KeyError:
            self._update_loc_rib(src_as, path, sureness)
            updated = True

        return updated

    def best_path(self, src_as: AS) -> ASPath:
        """Retrieves the selected path by the Loc-RIB of an AS.

        Args:
            src_as: The source AS.

        Returns: The ASPath.

        Raises:
            LocRIBManagerError: If there are no paths from src_as to dst_prefix.
        """
        try:
            return self._loc_ribs[src_as]
        except KeyError as e:
            raise LocRIBModelError(f"There is no Loc-RIB for {src_as}") from e

    def _update_loc_rib(self, src_as: AS, path: ASPath, sureness: bool) -> None:
        self._loc_ribs[src_as] = path
        self._sure_paths[src_as] = sureness

    def _generate_second_sure_path_event(
        self, target: AS, old_path: ASPath, new_path: ASPath
    ) -> None:
        event = SecondSurePathEvent(target, old_path, new_path)
        self._events.append(event)
