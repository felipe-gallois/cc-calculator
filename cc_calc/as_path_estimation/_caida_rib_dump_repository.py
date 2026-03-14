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


def _collect_prefix_paths(
    text: TextIO, prefixes: Iterable[IPPrefix]
) -> dict[IPPrefix, set[ASPath]]:
    mappings: dict[IPPrefix, set[ASPath]] = {prefix: set() for prefix in prefixes}

    for line in text:
        spaced_tokens = line.split(" ")

        prefix = IPPrefix(spaced_tokens[2])
        as_path = ASPath(spaced_tokens[1].split("|"))

        if prefix in mappings:
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

    def load_prefix_paths(
        self, prefixes: Iterable[IPPrefix]
    ) -> set[PrefixSureASPathList]:
        """Loads sure AS path lists for the informed prefixes.

        Returns: A set of sure AS path lists (one for each input prefix).

        Raises:
            RIBLoadingError: If the dump file cannot be read.
        """
        try:
            with bz2.open(self._path, "rt") as text:
                prefix_paths = _collect_prefix_paths(text, prefixes)
                return {
                    PrefixSureASPathList(prefix, as_set)
                    for prefix, as_set in prefix_paths.items()
                }
        except Exception as e:
            raise PrefixSureASPathListRepositoryError(
                "Could not read input file"
            ) from e
