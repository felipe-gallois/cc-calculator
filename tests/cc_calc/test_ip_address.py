import pytest

from cc_calc.ip_address import IPAddressError, IPv4Address


def test_valid_ipv4_address_can_be_created() -> None:
    IPv4Address("192.0.2.1")


def test_invalid_ipv4_address_raises_exception() -> None:
    with pytest.raises(IPAddressError):
        IPv4Address("192021")
