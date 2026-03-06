"""A repository for ASCountryMap objects."""

import gzip
from enum import Enum, auto
from os import PathLike
from typing import TextIO

from cc_calc.as_country_map import ASCountryMap
from cc_calc.autonomous_system import AS
from cc_calc.country import Country


class _CaidaParserState(Enum):
    IGNORING_LINES = auto()
    PARSING_COUNTRIES = auto()
    PARSING_ASNS = auto()


class _CaidaASCountryMapMapper:
    @staticmethod
    def text_to_asn_country_map(text: TextIO) -> dict[str, str]:
        org_id_to_country, asn_to_org_id = _CaidaASCountryMapMapper._get_org_maps(text)

        map: dict[str, str] = {}

        for asn, org_id in asn_to_org_id.items():
            country = org_id_to_country[org_id]
            map[asn] = country

        return map

    @staticmethod
    def _get_org_maps(text: TextIO) -> tuple[dict[str, str], dict[str, str]]:
        org_id_to_country: dict[str, str] = {}
        asn_to_org_id: dict[str, str] = {}

        state = _CaidaParserState.IGNORING_LINES

        for line in text:
            if line.startswith("# format:org_id"):
                state = _CaidaParserState.PARSING_COUNTRIES
                continue

            if line.startswith("# format:aut"):
                state = _CaidaParserState.PARSING_ASNS
                continue

            match state:
                case _CaidaParserState.PARSING_COUNTRIES:
                    org_id, country = _CaidaASCountryMapMapper._parse_org_line_info(
                        line
                    )
                    org_id_to_country[org_id] = country
                case _CaidaParserState.PARSING_ASNS:
                    asn, org_id = _CaidaASCountryMapMapper._parse_asn_line_info(line)
                    asn_to_org_id[asn] = org_id
                case _:
                    pass

        return org_id_to_country, asn_to_org_id

    @staticmethod
    def _parse_org_line_info(line: str) -> tuple[str, str]:
        tokens = line.split("|")
        org_id = tokens[0]
        country = tokens[3]
        return org_id, country

    @staticmethod
    def _parse_asn_line_info(line: str) -> tuple[str, str]:
        tokens = line.split("|")
        asn = tokens[0]
        org_id = tokens[3]
        return asn, org_id


class CaidaASCountryMapRepository:
    """CAIDA implementation of an AS-to-country map repository.

    This implementation is specific for the CAIDA AS Organizations Dataset.
    """

    def __init__(self, path: str | PathLike[str]) -> None:
        """Initializes the repository.

        Args:
            path: The path to the dataset file (text version).
        """
        self._path = path

    def load_map(self) -> ASCountryMap:
        """Loads the AS-to-country map from the repository.

        Returns: The map.
        """
        with gzip.open(self._path, "rt", encoding="utf-8") as text:
            asn_country_map = _CaidaASCountryMapMapper.text_to_asn_country_map(text)

        return ASCountryMap(
            {AS(asn): Country(country) for asn, country in asn_country_map.items()}
        )
