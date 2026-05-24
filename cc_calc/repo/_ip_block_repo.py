from abc import ABC, abstractmethod
from typing import Iterator

from cc_calc.core import (
    ASN,
    Alpha2Code,
    IPBlock,
    IPBlockSpecification,
    IPPrefix,
)

type ASNDTO = int
type CountryDTO = str
type IPPrefixDTO = str


class IPBlockLoadingError(Exception):
    def __init__(self) -> None:
        super().__init__("could not read from IP prefix database")


class IPPrefixDB(ABC):
    @abstractmethod
    def load_all_ip_prefixes(self) -> Iterator[IPPrefixDTO]:
        pass


class PrefixASNDB(ABC):
    @abstractmethod
    def load_prefix_asn(self, prefix: IPPrefixDTO) -> ASNDTO | None:
        pass


class PrefixCountryDB(ABC):
    @abstractmethod
    def load_prefix_country(self, prefix: IPPrefixDTO) -> CountryDTO | None:
        pass


class IPBlockRepo:
    def __init__(
        self,
        prefix_source: IPPrefixDB,
        asn_resolver: PrefixASNDB,
        country_resolver: PrefixCountryDB,
    ) -> None:
        self._prefix_source = prefix_source
        self._asn_resolver = asn_resolver
        self._country_resolver = country_resolver

        self._ip_blocks: set[IPBlock] | None = None

    def load_blocks_with_specs(self, specs: set[IPBlockSpecification]) -> set[IPBlock]:
        if self._ip_blocks is None:
            self._ip_blocks = self._get_blocks()

        blocks_with_specs = {
            block
            for block in self._ip_blocks
            if all(spec.is_met_in(block) for spec in specs)
        }

        return blocks_with_specs

    def _get_blocks(self) -> set[IPBlock]:
        prefixes = self._prefix_source.load_all_ip_prefixes()

        country_blocks = set()

        for prefix in prefixes:
            country = self._country_resolver.load_prefix_country(prefix)
            asn = self._asn_resolver.load_prefix_asn(prefix)
            block = IPBlockRepo._make_block(prefix, asn, country)
            country_blocks.add(block)

        return country_blocks

    @staticmethod
    def _make_block(prefix: str, asn: int | None, country: str | None) -> IPBlock:
        block = IPBlock(IPPrefix(prefix))

        block.autonomous_system = None if asn is None else ASN(asn)
        block.country = None if country is None else Alpha2Code(country)

        return block
