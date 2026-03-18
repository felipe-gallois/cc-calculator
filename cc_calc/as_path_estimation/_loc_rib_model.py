"""Simplified Loc-RIB model."""

from abc import ABC, abstractmethod
from copy import copy
from dataclasses import dataclass

from cc_calc.as_path_estimation._as_path import ASPath
from cc_calc.autonomous_system import AS
from cc_calc.ip_prefix import IPPrefix


class LocRIBModelError(Exception):
    """Any error raised by a Loc-RIB manager."""

    pass


class LocRIBModelRepositoryError(Exception):
    pass


class LocRIBModel:
    """A simplified Loc-RIB model for a single IP prefix.

    This class manages predicted Loc-RIB tables for different ASes (it simplifies the
    problem, assuming only one router per AS).

    It evaluates paths to IP prefixes announced by Adj-RIB-In tables, keeping only the
    best one for each AS, according to a simple heuristic in which the shorter paths are
    chosen over longer ones.
    """

    def __init__(self, prefix: IPPrefix) -> None:
        """Initializes the object.

        Args:
            prefix: The destination prefix for the stored AS paths.
        """
        self._prefix = IPPrefix
        self._loc_ribs: dict[AS, ASPath] = dict()

    def add_path(self, src_as: AS, path: ASPath) -> bool:
        """Adds a path to the Loc-RIB model.

        Args:
            src_as: The AS that receives the Adj-RIB-In path.
            path: The AS path to the prefix.

        Returns: A boolean, telling if the operation caused a best path update.
        """
        updated = False

        try:
            rib_path = self._loc_ribs[src_as]

            if len(rib_path) > len(path):
                self._loc_ribs[src_as] = path
                updated = True
        except KeyError:
            self._loc_ribs[src_as] = path
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


class LocRIBModelRepository(ABC):
    @abstractmethod
    def save_model(self, model: LocRIBModel) -> None:
        pass
