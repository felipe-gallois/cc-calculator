import gzip
import zlib
from os import PathLike
from typing import Iterator, TextIO

from cc_calc.repo import ASDB, ASDTO, InvalidDBDataFormat, UnreachableDB


class CaidaASOrgDB(ASDB):
    def __init__(self, org_path: str | PathLike[str]) -> None:
        self._org_path = org_path

    def load_all_ases(self) -> Iterator[ASDTO]:
        try:
            with gzip.open(self._org_path, "rt", encoding="utf-8") as file:
                asn_details_map = self._collect_map(file)

            for asn, country in asn_details_map.items():
                yield ASDTO(int(asn), country)
        except (FileNotFoundError, PermissionError) as e:
            raise UnreachableDB(str(self._org_path)) from e
        except gzip.BadGzipFile, EOFError, zlib.error, UnicodeDecodeError:
            raise InvalidDBDataFormat(str(self._org_path))

    def _collect_map(self, file: TextIO) -> dict[str, str]:
        try:
            reading_countries = False

            id_to_country = {}
            asn_to_id = {}

            for line in file:
                if line.startswith("# format:org_id"):
                    reading_countries = True
                elif line.startswith("# format:aut"):
                    reading_countries = False
                elif line.startswith("#"):
                    pass
                else:
                    tokens = line.split("|")

                    if reading_countries:
                        id_to_country[tokens[0]] = tokens[3]
                    else:
                        asn_to_id[tokens[0]] = tokens[3]

            return {
                asn: id_to_country[id]
                for asn, id in asn_to_id.items()
                if id in id_to_country
            }
        except IndexError:
            raise InvalidDBDataFormat(str(self._org_path))
