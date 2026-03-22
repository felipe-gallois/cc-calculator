from abc import ABC, abstractmethod

from cc_calc.country._ip_prefix_source import IPPrefixSource, IPPrefixSourceError
from cc_calc.country._prefix_asn_resolver import (
    PrefixASNResolver,
    PrefixASNResolverError,
)
from cc_calc.country._prefix_country_resolver import (
    PrefixCountryResolver,
    PrefixCountryResolverError,
)


class ASNResolverError(Exception):
    pass


class ASNResolver(ABC):
    @abstractmethod
    def load_country_asns(self, country: str) -> set[int]:
        pass


class FileASNResolver(ASNResolver):
    def __init__(
        self,
        prefix_source: IPPrefixSource,
        asn_resolver: PrefixASNResolver,
        country_resolver: PrefixCountryResolver,
    ) -> None:
        self._prefix_source = prefix_source
        self._asn_resolver = asn_resolver
        self._country_resolver = country_resolver

    def load_country_asns(self, country: str) -> set[int]:
        try:
            prefixes = list(self._prefix_source.load_all_ip_prefixes())

            asns = []
            countries = []

            for prefix in prefixes:
                asns.append(self._asn_resolver.load_prefix_asn(prefix))
                countries.append(self._country_resolver.load_prefix_country(prefix))

            return {
                asn
                for asn, c in zip(asns, countries)
                if c == country and asn is not None
            }
        except IPPrefixSourceError as e:
            raise ASNResolverError("Could not read the IP prefix list") from e
        except PrefixASNResolverError as e:
            raise ASNResolverError("Could not read the ASN lookup file") from e
        except PrefixCountryResolverError as e:
            raise ASNResolverError("Could not read the country lookup file") from e
