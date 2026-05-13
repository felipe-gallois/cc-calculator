import pytest

from cc_calc.core._autonomous_system_number import ASN
from cc_calc.core._as_specification import ASSpecification
from cc_calc.core._ip_block import IPBlock
from cc_calc.core._ip_prefix import IPPrefix


@pytest.fixture
def ip_block() -> IPBlock:
    ip_block = IPBlock(IPPrefix("192.0.2.0/24"))
    ip_block.autonomous_system = ASN(65536)
    return ip_block


def test_when_spec_is_met_in_block_returns_true(ip_block: IPBlock) -> None:
    spec = ASSpecification(ASN(65536))
    assert spec.is_met_in(ip_block)


def test_when_spec_is_not_met_in_block_returns_false(ip_block: IPBlock) -> None:
    spec = ASSpecification(ASN(65537))
    assert not spec.is_met_in(ip_block)
