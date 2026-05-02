from cc_calc.autonomous_system_number import ASN
from cc_calc.ip_block._ip_block import IPBlock, IPBlockSpecification


class ASSpecification(IPBlockSpecification):
    def __init__(self, asn: ASN) -> None:
        self._asn = asn

    def __hash__(self) -> int:
        return hash(self._asn)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ASSpecification):
            return False

        if self._asn == other._asn:
            return True

        return False

    def is_met_in(self, ip_block: IPBlock) -> bool:
        return True if ip_block.autonomous_system == self._asn else False
