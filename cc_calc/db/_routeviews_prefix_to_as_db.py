import gzip
import logging
import zlib
from os import PathLike
from typing import Iterator, TextIO

from cc_calc.repo import (
    InvalidDBDataFormat,
    IPPrefixDB,
    IPPrefixDTO,
    UnreachableDB,
)


class RouteViewsPrefixToASDB(IPPrefixDB):
    logger = logging.getLogger(__name__)

    def __init__(self, path: str | PathLike[str]) -> None:
        self._path = path

    def load_all_ip_prefixes(self) -> Iterator[IPPrefixDTO]:
        try:
            with gzip.open(self._path, "rt", encoding="utf-8") as text:
                yield from self._yield_prefixes(text)
        except (FileNotFoundError, PermissionError) as e:
            raise UnreachableDB(str(self._path)) from e
        except gzip.BadGzipFile, EOFError, zlib.error, UnicodeDecodeError:
            raise InvalidDBDataFormat(str(self._path))

    def _yield_prefixes(self, text: TextIO) -> Iterator[IPPrefixDTO]:
        for line in text:
            try:
                tokens = line.split()
                yield tokens[0] + "/" + tokens[1]
            except IndexError:
                RouteViewsPrefixToASDB.logger.warning(
                    "IP prefix loading: skipping malformed file entry"
                )
                continue
