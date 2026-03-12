"""List of sure AS paths to a prefix."""

from collections.abc import Iterable, Iterator

from cc_calc.as_path import ASPath
from cc_calc.ip_prefix import IPPrefix


class PrefixSureASPathList:
    """List of sure AS paths to a prefix."""

    def __init__(self, prefix: IPPrefix, paths: Iterable[ASPath] = set()) -> None:
        self._prefix = prefix
        self._path_set = {path for path in paths}

    def __len__(self) -> int:
        return len(self._path_set)

    def __iter__(self) -> Iterator[ASPath]:
        for path in self._path_set:
            yield path

    @property
    def prefix(self) -> IPPrefix:
        """The prefix where the AS paths lead to."""
        return self._prefix

    def add_path(self, path: ASPath) -> None:
        """Adds a path to the list.

        Args:
            path: The path.
        """
        self._path_set.add(path)
