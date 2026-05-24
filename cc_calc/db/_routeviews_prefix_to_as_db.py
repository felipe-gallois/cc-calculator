import gzip
from os import PathLike
from typing import Iterator

from cc_calc.repo._ip_block_repo import (
    IPBlockLoadingError,
    IPPrefixDB,
    IPPrefixDTO,
)


class RouteViewsPrefixToASDB(IPPrefixDB):
    def __init__(self, path: str | PathLike[str]) -> None:
        self._path = path

    def load_all_ip_prefixes(self) -> Iterator[IPPrefixDTO]:
        try:
            with gzip.open(self._path, "rt", encoding="utf-8") as text:
                for line in text:
                    tokens = line.split("\t")
                    yield tokens[0] + "/" + tokens[1]
        except Exception as e:
            raise IPBlockLoadingError() from e
