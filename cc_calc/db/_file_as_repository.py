import gzip
import zlib
from os import PathLike
from typing import TextIO

from cc_calc.core import (
    Alpha2Code,
    AS,
    ASN,
    ASRepository,
    ASRepositoryError,
)


class FileASRepository(ASRepository):
    def __init__(self, org_path: str | PathLike[str]) -> None:
        self._org_path = org_path

    def load_as(self, asn: ASN) -> AS:
        try:
            with gzip.open(self._org_path, "rt", encoding="utf-8") as file:
                id_to_country, asn_to_id = FileASRepository._collect_maps(file)
                id = asn_to_id[str(asn)]
                country = id_to_country[id]
                return AS(asn, Alpha2Code(country))
        except (OSError, gzip.BadGzipFile, EOFError, zlib.error) as e:
            raise ASRepositoryError("Could not read data from file") from e
        except KeyError as e:
            raise ASRepositoryError(f"{asn} is not in file") from e

    @staticmethod
    def _collect_maps(file: TextIO) -> tuple[dict[str, str], dict[str, str]]:
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

        return id_to_country, asn_to_id
