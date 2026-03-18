"""Loading of sure AS paths."""

import bz2
from collections.abc import Iterable
from os import PathLike
from typing import TextIO

from cc_calc.as_path_estimation._as_path import ASPath
from cc_calc.as_path_estimation._prefix_sure_as_path_list import (
    PrefixSureASPathList,
    PrefixSureASPathListRepository,
    PrefixSureASPathListRepositoryError,
)
from cc_calc.ip_prefix import IPPrefix


def _collect_prefix_paths(text: TextIO) -> dict[IPPrefix, set[ASPath]]:
    mappings: dict[IPPrefix, set[ASPath]] = dict()

    for line in text:
        spaced_tokens = line.split(" ")

        if len(spaced_tokens) < 3:
            continue

        prefix = IPPrefix(spaced_tokens[2])
        as_path = ASPath(spaced_tokens[1].split("|"))

        if prefix not in mappings:
            mappings[prefix] = set()

        mappings[prefix].add(as_path)

    return mappings


class CaidaRIBDumpRepository(PrefixSureASPathListRepository):
    """A loader for sure AS paths found in CAIDA's RIB dumps."""

    def __init__(self, path: str | PathLike[str]) -> None:
        """Initializes the loader object.

        Args:
            path: The path to the "paths" database file.
        """
        self._path = path

    def load_all_sure_path_lists(self) -> set[PrefixSureASPathList]:
        """Loads every sure AS path list.

        Returns: A collection of every sure AS path list.

        Raises:
            RIBLoadingError: If the dump file cannot be read.
        """
        try:
            with bz2.open(self._path, "rt") as text:
                prefix_paths = _collect_prefix_paths(text)
                return {
                    PrefixSureASPathList(prefix, as_set)
                    for prefix, as_set in prefix_paths.items()
                }
        except Exception as e:
            raise PrefixSureASPathListRepositoryError(
                "Could not read input file"
            ) from e
