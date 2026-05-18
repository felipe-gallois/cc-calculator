import gzip
import logging
from abc import ABC, abstractmethod
from os import PathLike

from cc_calc.core import IPBlockLoadingError

logger = logging.getLogger(__name__)


class IPPrefixSource(ABC):
    @abstractmethod
    def load_all_ip_prefixes(self) -> set[str]:
        pass


class RouteViewsIPPrefixSource(IPPrefixSource):
    def __init__(self, path: str | PathLike[str]) -> None:
        self._path = path

    def load_all_ip_prefixes(self) -> set[str]:
        prefix_set = set()

        try:
            with gzip.open(self._path, "rt", encoding="utf-8") as text:
                for line in text:
                    tokens = line.split("\t")
                    prefix_set.add(tokens[0] + "/" + tokens[1])
        except Exception as e:
            message = "Failed loading IP prefix list: could not read input file"
            logger.error(message)
            raise IPBlockLoadingError(message) from e

        logger.info("Loaded IP prefix list")

        return prefix_set
