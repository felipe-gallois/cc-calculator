from cc_calc.autonomous_system._autonomous_system import AS
from cc_calc.autonomous_system_number import ASN
from cc_calc.country_code import Alpha2Code


def test_when_country_of_registry_is_br_returns_br() -> None:
    _as = AS(ASN(65536), Alpha2Code("BR"))
    assert _as.country_of_registry == Alpha2Code("BR")


def test_when_country_of_registry_is_us_returns_us() -> None:
    _as = AS(ASN(65536), Alpha2Code("US"))
    assert _as.country_of_registry == Alpha2Code("US")
