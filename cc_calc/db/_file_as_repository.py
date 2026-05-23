import gzip
import logging
import zlib
from os import PathLike
from typing import TextIO

from cc_calc.core import (
    AS,
    ASN,
    Alpha2Code,
    ASLoadingError,
    ASRepository,
)

logger = logging.getLogger(__name__)


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


class FileASRepository(ASRepository):
    def __init__(self, org_path: str | PathLike[str]) -> None:
        self._org_path = org_path
        self._as_map: dict[ASN, Alpha2Code] | None = None

    def load_as(self, asn: ASN) -> AS:
        try:
            if self._as_map is None:
                self._as_map = self._get_as_map()

            return AS(asn, self._as_map[asn])
        except KeyError as e:
            message = "Failed loading AS data: AS is not in input file"
            logger.error(message, extra={"asn": asn})
            raise ASLoadingError(message) from e

    def _get_as_map(self) -> dict[ASN, Alpha2Code]:
        try:
            with gzip.open(self._org_path, "rt", encoding="utf-8") as file:
                id_to_country, asn_to_id = _collect_maps(file)

            return {
                ASN(asn): Alpha2Code(id_to_country[id]) for asn, id in asn_to_id.items()
            }

            logger.info("Loaded world ASes")
        except (OSError, gzip.BadGzipFile, EOFError, zlib.error) as e:
            message = "Failed loading world ASes data: could not read data from file"
            logger.error(message)
            raise ASLoadingError(message) from e
