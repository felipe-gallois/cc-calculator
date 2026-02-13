"""Loading of RIB entries."""

import bz2
from os import PathLike
from typing import TextIO

from cc_calc.bgp_simulation import AS, AdjRIBLoader, IPPrefix, RIBLoadingError


class CaidaRIBLoader(AdjRIBLoader):
    """A loader for Adj-RIB-In entries found in CAIDA's RIB dumps."""

    def __init__(self, path: str | PathLike[str]) -> None:
        """Initializes the loader object.

        Args:
            path: The path to the "paths" database file.
        """
        self._path = path

    def load_prefix_paths(self) -> dict[IPPrefix, list[list[AS]]]:
        """Loads entries from CAIDA RIB dumps and maps prefixes to announced paths.

        Loads Adj-RIB-In entries gathered in the previously informed "paths" file of
        CAIDA's AS Relationship dataset and creates mappings between prefixes and paths
        that lead to them.

        Returns: A dict, mapping IP prefixes to a collection of AS paths.

        Raises:
            RIBLoadingError: If the dump file cannot be read.
        """
        try:
            with bz2.open(self._path, "rt") as text:
                return CaidaRIBLoader._parse_entries(text)
        except Exception as e:
            raise RIBLoadingError("Could not read input file") from e

    @staticmethod
    def _parse_entries(text: TextIO) -> dict[IPPrefix, list[list[AS]]]:
        mappings: dict[IPPrefix, list[list[AS]]] = {}

        for line in text:
            spaced_tokens = line.split(" ")

            prefix = IPPrefix(spaced_tokens[2])
            as_path = spaced_tokens[1].split("|")

            if prefix not in mappings:
                mappings[prefix] = []

            mappings[prefix].append(as_path)

        return mappings
