import bz2
import logging
from os import PathLike
from typing import Iterator, TextIO

from cc_calc.repo import (
    ASNDB,
    ASNDTO,
    ASRelDB,
    ASRelDTO,
    InvalidDBDataFormat,
    RelTypeDTO,
    UnreachableDB,
)


class CaidaASRelDB(ASNDB, ASRelDB):
    logger = logging.getLogger(__name__)

    def __init__(self, path: str | PathLike[str]) -> None:
        self._path = path

    def load_rels(self) -> Iterator[ASRelDTO]:
        try:
            with bz2.open(self._path, mode="rt", encoding="utf-8") as text:
                yield from self._yield_as_rel_dtos(text)
        except (FileNotFoundError, PermissionError) as e:
            raise UnreachableDB(str(self._path)) from e
        except (OSError, UnicodeDecodeError, ValueError) as e:
            raise InvalidDBDataFormat(str(self._path)) from e

    def load_all_asns(self) -> Iterator[ASNDTO]:
        try:
            with bz2.open(self._path, mode="rt", encoding="utf-8") as text:
                yield from self._yield_asn_dtos(text)
        except (FileNotFoundError, PermissionError) as e:
            raise UnreachableDB(str(self._path)) from e
        except (OSError, UnicodeDecodeError, ValueError) as e:
            raise InvalidDBDataFormat(str(self._path)) from e

    def _yield_as_rel_dtos(self, text: TextIO) -> Iterator[ASRelDTO]:
        for line in text:
            try:
                tokens = line.split("|")

                if len(tokens) < 3 or line.startswith("#"):
                    yield from ()
                else:
                    rel_type = self._get_rel_type_from_string(tokens[2])
                    yield ASRelDTO(int(tokens[0]), int(tokens[1]), rel_type)
            except ValueError, InvalidDBDataFormat:
                CaidaASRelDB.logger.warning(
                    "AS rel loading: skipping malformed file entry"
                )
                continue

    def _yield_asn_dtos(self, text: TextIO) -> Iterator[ASNDTO]:
        for line in text:
            tokens = line.split("|")

            if len(tokens) < 3 or line.startswith("#"):
                yield from ()
            else:
                for i in [0, 1]:
                    try:
                        yield int(tokens[i])
                    except ValueError:
                        CaidaASRelDB.logger.warning(
                            "ASN loading: skipping malformed file entry"
                        )
                        continue

    def _get_rel_type_from_string(self, value: str) -> RelTypeDTO:
        rel_type_int = int(value)

        if rel_type_int == 0:
            return RelTypeDTO.P2P

        if rel_type_int == -1:
            return RelTypeDTO.P2C

        raise InvalidDBDataFormat(str(self._path))
