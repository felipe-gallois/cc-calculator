from cc_calc.country_code import CountryCode
from cc_calc.ip_block._ip_block import IPBlock, IPBlockSpecification


class CountrySpecification(IPBlockSpecification):
    def __init__(self, country: CountryCode) -> None:
        self._country = country

    def is_met_in(self, ip_block: IPBlock) -> bool:
        return True if ip_block.country == self._country else False
