from cc_calc.core import (
    Alpha2Code,
    ASN,
    IPBlock,
    IPBlockRepository,
    IPBlockRepositoryError,
    IPBlockSpecification,
    IPPrefix,
)
from cc_calc.db._ip_prefix_source import IPPrefixSource, IPPrefixSourceError
from cc_calc.db._prefix_asn_resolver import (
    PrefixASNResolver,
    PrefixASNResolverError,
)
from cc_calc.db._prefix_country_resolver import (
    PrefixCountryResolver,
    PrefixCountryResolverError,
)


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
        try:
            prefixes = self._prefix_source.load_all_ip_prefixes()

            country_blocks = set()

            for prefix in prefixes:
                country = self._country_resolver.load_prefix_country(prefix)
                asn = self._asn_resolver.load_prefix_asn(prefix)
                block = FileIPBlockRepository._make_block(prefix, asn, country)

                if all(spec.is_met_in(block) for spec in specs):
                    country_blocks.add(block)

            return country_blocks
        except IPPrefixSourceError as e:
            raise IPBlockRepositoryError("Could not read the IP prefix list") from e
        except PrefixASNResolverError as e:
            raise IPBlockRepositoryError("Could not read the ASN lookup file") from e
        except PrefixCountryResolverError as e:
            raise IPBlockRepositoryError(
                "Could not read the country lookup file"
            ) from e

    @staticmethod
    def _make_block(prefix: str, asn: int | None, country: str | None) -> IPBlock:
        block = IPBlock(IPPrefix(prefix))

        block.autonomous_system = None if asn is None else ASN(asn)
        block.country = None if country is None else Alpha2Code(country)

        return block
