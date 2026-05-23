import pytest

from cc_calc.core._autonomous_system import AS
from cc_calc.core._autonomous_system_number import ASN
from cc_calc.core._country_code import Alpha2Code


@pytest.fixture
def _as() -> AS:
    return AS(ASN(65536))


@pytest.mark.parametrize("asn", [ASN(65536), ASN(65537)])
def test_asn_is_returned_correctly(asn: ASN) -> None:
    _as = AS(asn)
    assert _as.asn == asn


def test_when_comparing_object_is_not_an_as_it_returns_not_equal(_as: AS) -> None:
    other = 65536
    assert _as != other


def test_when_comparing_as_has_the_same_asn_returns_equal(_as: AS) -> None:
    other = AS(ASN(65536))
    assert _as == other


def test_when_comparing_as_does_not_have_the_same_asn_returns_not_equal(
    _as: AS,
) -> None:
    other = AS(ASN(65537))
    assert _as != other


@pytest.mark.parametrize("asn", [ASN(65536), ASN(65537)])
def test_as_has_is_asn_hash(asn: ASN) -> None:
    _as = AS(asn)
    assert hash(_as) == hash(asn)


def test_when_as_is_created_country_of_registry_starts_none(_as: AS) -> None:
    assert _as.country_of_registry is None


def test_when_country_of_registry_is_assigned_property_returns_it(_as: AS) -> None:
    country = Alpha2Code("BR")
    _as.country_of_registry = country
    assert _as.country_of_registry == country
