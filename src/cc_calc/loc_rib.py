"""Utilities for simulating Loc-RIB tables."""

from dataclasses import dataclass

from cc_calc.autonomous_system import AS, ASPath
from cc_calc.ip_prefix import IPv4Prefix, IPv6Prefix


class LocRIBManagerError(Exception):
    """Any error raised by a Loc-RIB manager."""

    pass


class _LocRIBError(Exception):
    """Any error raised by a Loc-RIB."""

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


class _SimpleLocRIB:
    """A simple Loc-RIB table representation."""

    def __init__(self) -> None:
        self._entries: dict[IPv4Prefix | IPv6Prefix, _SimpleLocRIBDetails] = dict()

    def __getitem__(self, index: IPv4Prefix | IPv6Prefix) -> _SimpleLocRIBDetails:
        try:
            return self._entries[index]
        except KeyError as e:
            raise _LocRIBError(f"Tried accessing non-existent path to {index}.") from e

    def __setitem__(
        self, index: IPv4Prefix | IPv6Prefix, value: _SimpleLocRIBDetails
    ) -> None:
        self._entries[index] = value

    def __delitem__(self, index: IPv4Prefix | IPv6Prefix) -> None:
        try:
            del self._entries[index]
        except KeyError as e:
            raise _LocRIBError(f"Tried deleting non-existent path to {index}.") from e


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
        self._ribs: dict[AS, _SimpleLocRIB] = dict()

    def eval_sure_path_recursively(
        self, dst_prefix: IPv4Prefix | IPv6Prefix, path: ASPath
    ) -> None:
        """Adds sure paths recursively to Loc-RIB tables.

        Given one sure AS path, every sub-path is also sure. Thus, this function
        recursively adds each subpath to the Loc-RIB tables.

        Args:
            src_as: The AS that receives the Adj-RIB-In path.
            dst_prefix: The destination prefix.
            path: The AS path to the prefix.
        """
        for i in range(len(path)):
            self._eval_sure_path(path[i], dst_prefix, path[i + 1 :])  # type: ignore

    def eval_unsure_path(
        self, src_as: AS, dst_prefix: IPv4Prefix | IPv6Prefix, path: ASPath
    ) -> None:
        """Adds an unsure path to a Loc-RIB table.

        Args:
            src_as: The AS that receives the Adj-RIB-In path.
            dst_prefix: The destination prefix.
            path: The AS path to the prefix.
        """
        try:
            entry = self._ribs[src_as][dst_prefix]

            if (not entry.is_sure) and (len(entry.path) > len(path)):
                self._ribs[src_as][dst_prefix] = _SimpleLocRIBDetails(
                    path, is_sure=False
                )
        except KeyError:
            self._ribs[src_as] = _SimpleLocRIB()
            self._ribs[src_as][dst_prefix] = _SimpleLocRIBDetails(path, is_sure=False)
        except _LocRIBError:
            self._ribs[src_as][dst_prefix] = _SimpleLocRIBDetails(path, is_sure=False)

    def best_path(self, src_as: AS, dst_prefix: IPv4Prefix | IPv6Prefix) -> ASPath:
        """Retrieves the selected path by the Loc-RIB of an AS.

        Args:
            src_as: The source AS.
            dst_prefix: The destination prefix.

        Returns: The ASPath.

        Raises:
            LocRIBManagerError: If there are no paths from src_as to dst_prefix.
        """
        try:
            return self._ribs[src_as][dst_prefix].path
        except KeyError as e:
            raise LocRIBManagerError(f"There is no Loc-RIB for {src_as}") from e
        except _LocRIBError as e:
            raise LocRIBManagerError(
                f"No path found between {src_as} and {dst_prefix}"
            ) from e

    def _eval_sure_path(
        self, src_as: AS, dst_prefix: IPv4Prefix | IPv6Prefix, path: ASPath
    ) -> None:
        try:
            entry = self._ribs[src_as][dst_prefix]

            if (not entry.is_sure) or (len(entry.path) > len(path)):
                self._ribs[src_as][dst_prefix] = _SimpleLocRIBDetails(
                    path, is_sure=True
                )
        except KeyError:
            self._ribs[src_as] = _SimpleLocRIB()
            self._ribs[src_as][dst_prefix] = _SimpleLocRIBDetails(path, is_sure=True)
        except _LocRIBError:
            self._ribs[src_as][dst_prefix] = _SimpleLocRIBDetails(path, is_sure=True)
