from cc_calc.country_code import CountryCode
from cc_calc.ip_block._ip_block import (
    IPBlock,
    IPBlockRepository,
    IPBlockRepositoryError,
)
from cc_calc.ip_block._ip_prefix_source import IPPrefixSource, IPPrefixSourceError
from cc_calc.ip_block._prefix_country_resolver import (
    PrefixCountryResolver,
    PrefixCountryResolverError,
)
from cc_calc.ip_prefix import IPPrefix


class FileIPBlockRepository(IPBlockRepository):
    def __init__(
        self,
        prefix_source: IPPrefixSource,
        country_resolver: PrefixCountryResolver,
    ) -> None:
        self._prefix_source = prefix_source
        self._country_resolver = country_resolver

    def load_blocks_in_country(self, country: CountryCode) -> set[IPBlock]:
        try:
            prefixes = list(self._prefix_source.load_all_ip_prefixes())

            countries = []

            for prefix in prefixes:
                countries.append(self._country_resolver.load_prefix_country(prefix))

            return {
                IPBlock(IPPrefix(prefix))
                for prefix, c in zip(prefixes, countries)
                if c == str(country)
            }
        except IPPrefixSourceError as e:
            raise IPBlockRepositoryError("Could not read the IP prefix list") from e
        except PrefixCountryResolverError as e:
            raise IPBlockRepositoryError(
                "Could not read the country lookup file"
            ) from e
