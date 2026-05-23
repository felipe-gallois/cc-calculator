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
            block = FileIPBlockRepository._make_block(prefix, asn, country)
            country_blocks.add(block)

        return country_blocks

    @staticmethod
    def _make_block(prefix: str, asn: int | None, country: str | None) -> IPBlock:
        block = IPBlock(IPPrefix(prefix))

        block.autonomous_system = None if asn is None else ASN(asn)
        block.country = None if country is None else Alpha2Code(country)

        return block
