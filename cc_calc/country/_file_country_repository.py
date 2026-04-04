from cc_calc.autonomous_system_number import ASN
from cc_calc.country._asn_resolver import ASNResolver, ASNResolverError
from cc_calc.country._country import Country, CountryRepository, CountryRepositoryError
from cc_calc.country._country_code import CountryCode


class FileCountryRepository(CountryRepository):
    def __init__(self, asn_resolver: ASNResolver) -> None:
        self._asn_resolver = asn_resolver

    def load_country_with_code(self, code: CountryCode) -> Country:
        try:
            asns = self._asn_resolver.load_country_asns(str(code))

            country = Country(code)
            for asn in asns:
                country.add_as(ASN(asn))

            return country
        except ASNResolverError as e:
            raise CountryRepositoryError(
                "Could not load country's autonomous systems"
            ) from e
