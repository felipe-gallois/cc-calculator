import pytest

from cc_calc.core._country_code import Alpha2Code
from cc_calc.core._country_specification import CountrySpecification
from cc_calc.core._ip_block import IPBlock
from cc_calc.core._ip_prefix import IPPrefix


@pytest.fixture
def ip_block() -> IPBlock:
    ip_block = IPBlock(IPPrefix("192.0.2.0/24"))
    ip_block.country = Alpha2Code("BR")
    return ip_block


def test_when_spec_is_met_returns_true(ip_block: IPBlock) -> None:
    spec = CountrySpecification(Alpha2Code("BR"))
    assert spec.is_met_in(ip_block)


def test_when_spec_is_not_met_returns_false(ip_block: IPBlock) -> None:
    spec = CountrySpecification(Alpha2Code("US"))
    assert not spec.is_met_in(ip_block)
