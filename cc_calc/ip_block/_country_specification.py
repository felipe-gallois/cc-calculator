from cc_calc.country_code import CountryCode
from cc_calc.ip_block._ip_block import IPBlock, IPBlockSpecification


class CountrySpecification(IPBlockSpecification):
    def __init__(self, country: CountryCode) -> None:
        self._country = country

    def __hash__(self) -> int:
        return hash(self._country)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CountrySpecification):
            return False

        if self._country == other._country:
            return True

        return False

    def is_met_in(self, ip_block: IPBlock) -> bool:
        return True if ip_block.country == self._country else False
