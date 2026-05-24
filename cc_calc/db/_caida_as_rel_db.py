import bz2
from os import PathLike
from typing import Iterator

from cc_calc.repo import ASRelDB, ASRelDTO, ASRelLoadingError, RelTypeDTO


class CaidaASRelDB(ASRelDB):
    def __init__(self, path: str | PathLike[str]) -> None:
        self._path = path

    def load_rels(self) -> Iterator[ASRelDTO]:
        try:
            with bz2.open(self._path, mode="rt", encoding="utf-8") as text:
                for line in text:
                    tokens = line.split("|")

                    if len(tokens) < 3 or line.startswith("#"):
                        yield from ()
                    else:
                        rel_type = CaidaASRelDB._get_rel_type_from_string(tokens[2])
                        yield ASRelDTO(int(tokens[0]), int(tokens[1]), rel_type)
        except Exception as e:
            raise ASRelLoadingError() from e

    @staticmethod
    def _get_rel_type_from_string(value: str) -> RelTypeDTO:
        rel_type_int = int(value)
        return RelTypeDTO.P2P if rel_type_int == 0 else RelTypeDTO.P2C
