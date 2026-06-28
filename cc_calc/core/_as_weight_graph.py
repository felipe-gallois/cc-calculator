from collections import Counter

from cc_calc.core._autonomous_system_number import ASN
from cc_calc.core._country_code import CountryCode
from cc_calc.core._ip_block import IPBlock


class ASWeightGraph:
    def __init__(self) -> None:
        self._weights: dict[ASN, Counter[CountryCode]] = dict()

    def is_null(self) -> bool:
        return len(self._weights) == 0

    def add_ip_block(self, ip_block: IPBlock) -> None:
        autonomous_system = ip_block.autonomous_system
        country = ip_block.country

        if autonomous_system is not None and country is not None:
            if autonomous_system not in self._weights.keys():
                self._weights[autonomous_system] = Counter()

            self._weights[autonomous_system][country] += 2 ** (
                32 - ip_block.prefix.n_bits
            )

    def get_as_weights(self, asn: ASN) -> dict[CountryCode, int]:
        try:
            return dict(self._weights[asn])
        except KeyError:
            return dict()
