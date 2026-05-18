import logging

from cc_calc.core import (
    ASN,
    Alpha2Code,
    IPBlock,
    IPBlockRepository,
    IPBlockSpecification,
    IPPrefix,
)
from cc_calc.db._ip_prefix_source import IPPrefixSource
from cc_calc.db._prefix_asn_resolver import PrefixASNResolver
from cc_calc.db._prefix_country_resolver import PrefixCountryResolver

logger = logging.getLogger(__name__)


class FileIPBlockRepository(IPBlockRepository):
    def __init__(
        self,
        prefix_source: IPPrefixSource,
        asn_resolver: PrefixASNResolver,
        country_resolver: PrefixCountryResolver,
    ) -> None:
        self._prefix_source = prefix_source
        self._asn_resolver = asn_resolver
        self._country_resolver = country_resolver

    def load_blocks_with_specs(self, specs: set[IPBlockSpecification]) -> set[IPBlock]:
        prefixes = self._prefix_source.load_all_ip_prefixes()

        country_blocks = set()

        for prefix in prefixes:
            country = self._country_resolver.load_prefix_country(prefix)
            asn = self._asn_resolver.load_prefix_asn(prefix)
            block = FileIPBlockRepository._make_block(prefix, asn, country)

            if all(spec.is_met_in(block) for spec in specs):
                country_blocks.add(block)

        logger.info("Loaded IP blocks with specs", extra={"specs": specs})

        return country_blocks

    @staticmethod
    def _make_block(prefix: str, asn: int | None, country: str | None) -> IPBlock:
        block = IPBlock(IPPrefix(prefix))

        block.autonomous_system = None if asn is None else ASN(asn)
        block.country = None if country is None else Alpha2Code(country)

        return block
