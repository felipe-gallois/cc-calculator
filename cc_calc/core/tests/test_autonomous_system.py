import pytest

from cc_calc.core._autonomous_system import AS
from cc_calc.core._autonomous_system_number import ASN
from cc_calc.core._country_code import Alpha2Code


@pytest.mark.parametrize("asn", [ASN(65536), ASN(65537)])
def test_asn_is_returned_correctly(asn: ASN) -> None:
    _as = AS(asn)
    assert _as.asn == asn


def test_when_as_is_created_country_of_registry_starts_none() -> None:
    _as = AS(ASN(65536))
    assert _as.country_of_registry is None


def test_when_country_of_registry_is_assigned_property_returns_it() -> None:
    _as = AS(ASN(65536))
    country = Alpha2Code("BR")
    _as.country_of_registry = country
    assert _as.country_of_registry == country
