from cc_calc.autonomous_system_number import ASN
from cc_calc.ip_block._ip_block import IPBlock, IPBlockSpecification


class ASSpecification(IPBlockSpecification):
    def __init__(self, asn: ASN) -> None:
        self._asn = asn

    def is_met_in(self, ip_block: IPBlock) -> bool:
        return True if ip_block.autonomous_system == self._asn else False
