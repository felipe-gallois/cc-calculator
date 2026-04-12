from cc_calc.autonomous_system_number import ASN
from cc_calc.country_code import Alpha2Code, CountryCode
from cc_calc.ip_block._ip_block import (
    IPBlock,
    IPBlockRepository,
    IPBlockRepositoryError,
)
from cc_calc.ip_block._ip_prefix_source import IPPrefixSource, IPPrefixSourceError
from cc_calc.ip_block._prefix_asn_resolver import (
    PrefixASNResolver,
    PrefixASNResolverError,
)
from cc_calc.ip_block._prefix_country_resolver import (
    PrefixCountryResolver,
    PrefixCountryResolverError,
)
from cc_calc.ip_prefix import IPPrefix


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

    def load_blocks_in_country(self, country: CountryCode) -> set[IPBlock]:
        try:
            prefixes = self._prefix_source.load_all_ip_prefixes()

            country_blocks = set()

            for prefix in prefixes:
                c = self._country_resolver.load_prefix_country(prefix)

                if c == str(country):
                    asn = self._asn_resolver.load_prefix_asn(prefix)

                    block = FileIPBlockRepository._make_block(prefix, asn, c)
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
