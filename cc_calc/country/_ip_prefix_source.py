import gzip
from abc import ABC, abstractmethod
from os import PathLike


class IPPrefixSourceError(Exception):
    pass


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
            raise IPPrefixSourceError("Could not read from IP prefix source") from e

        return prefix_set
