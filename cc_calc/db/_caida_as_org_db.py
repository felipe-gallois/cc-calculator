import gzip
from os import PathLike
from typing import Iterator, TextIO

from cc_calc.core import (
    ASLoadingError,
)
from cc_calc.repo import ASDB, ASDTO


class CaidaASOrgDB(ASDB):
    def __init__(self, org_path: str | PathLike[str]) -> None:
        self._org_path = org_path

    def load_all_ases(self) -> Iterator[ASDTO]:
        try:
            with gzip.open(self._org_path, "rt", encoding="utf-8") as file:
                asn_details_map = self._collect_map(file)

            for asn, country in asn_details_map.items():
                yield ASDTO(int(asn), country)
        except Exception as e:
            raise ASLoadingError() from e

    @staticmethod
    def _collect_map(file: TextIO) -> dict[str, str]:
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

        return {asn: id_to_country[id] for asn, id in asn_to_id.items()}
