"""Utilities for simulating Loc-RIB tables."""

from dataclasses import dataclass

from cc_calc.as_path import ASPath
from cc_calc.autonomous_system import AS


class LocRIBManagerError(Exception):
    """Any error raised by a Loc-RIB manager."""

    pass


@dataclass
class _SimpleLocRIBDetails:
    """Details of an AS-prefix path.

    Attributes:
        path: The AS-level path from the AS to the prefix.
        is_sure: A boolean that indicates if the path is sure or not.
    """

    path: ASPath
    is_sure: bool


class SimpleLocRIBManager:
    """A simple Loc-RIB table manager.

    This class creates and manages Loc-RIB tables for different ASes (it simplifies the
    problem, assuming only one router per AS).

    It evaluates paths to IP prefixes announced by Adj-RIB-In tables, keeping only the
    best one for each AS, according to some simple heuristics, and considering that some
    Adj-RIB-In entries are sure, while others are infered. The heuristics for selecting
    the best path are summarized as follows: the shorter paths are chosen over longer
    ones, but the sure paths are always given preference over unsure ones.
    """

    def __init__(self) -> None:
        """Initiliazes the object."""
        self._performed_unsure_update = False
        self._ribs: dict[AS, _SimpleLocRIBDetails] = dict()

    @property
    def performed_unsure_update(self) -> bool:
        """Whether the last unsure path evaluation caused a Loc-RIB update."""
        return self._performed_unsure_update

    def eval_sure_path_recursively(self, path: ASPath) -> None:
        """Adds sure paths recursively to Loc-RIB tables.

        Given one sure AS path, every sub-path is also sure. Thus, this function
        recursively adds each subpath to the Loc-RIB tables.

        Args:
            path: The AS path to the prefix.
        """
        for i in range(len(path)):
            last_as = path[i]

            if last_as is not None:
                self._eval_sure_path(last_as, path[i + 1 :])

    def eval_unsure_path(self, src_as: AS, path: ASPath) -> None:
        """Adds an unsure path to a Loc-RIB table.

        Args:
            src_as: The AS that receives the Adj-RIB-In path.
            path: The AS path to the prefix.
        """
        try:
            entry = self._ribs[src_as]

            if (not entry.is_sure) and (len(entry.path) > len(path)):
                self._ribs[src_as].path = path
                self._ribs[src_as].is_sure = False
                self._performed_unsure_update = True
            else:
                self._performed_unsure_update = False
        except KeyError:
            self._ribs[src_as] = _SimpleLocRIBDetails(path, is_sure=False)
            self._performed_unsure_update = True

    def best_path(self, src_as: AS) -> ASPath:
        """Retrieves the selected path by the Loc-RIB of an AS.

        Args:
            src_as: The source AS.

        Returns: The ASPath.

        Raises:
            LocRIBManagerError: If there are no paths from src_as to dst_prefix.
        """
        try:
            return self._ribs[src_as].path
        except KeyError as e:
            raise LocRIBManagerError(f"There is no Loc-RIB for {src_as}") from e

    def _eval_sure_path(self, src_as: AS, path: ASPath) -> None:
        try:
            entry = self._ribs[src_as]

            if (not entry.is_sure) or (len(entry.path) > len(path)):
                self._ribs[src_as].path = path
                self._ribs[src_as].is_sure = True
        except KeyError:
            self._ribs[src_as] = _SimpleLocRIBDetails(path, is_sure=True)
