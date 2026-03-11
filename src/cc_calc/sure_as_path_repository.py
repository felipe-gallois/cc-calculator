"""Sure AS path repository abstraction."""

from abc import ABC, abstractmethod
from collections.abc import Iterable

from cc_calc.ip_prefix import IPPrefix
from cc_calc.prefix_sure_as_path_list import PrefixSureASPathList


class SureASPathRepositoryError(Exception):
    """Any error raised by a SureASPathRepository."""

    pass


class SureASPathRepository(ABC):
    """An abstraction for a sure AS path repository."""

    @abstractmethod
    def load_prefix_paths(
        self, prefixes: Iterable[IPPrefix]
    ) -> set[PrefixSureASPathList]:
        """Loads sure AS path lists for the input prefixes.

        Returns: A set of sure AS path lists (one for each input prefix).

        Raises:
            RIBLoadingError: If the dump file cannot be read.
        """
        pass
