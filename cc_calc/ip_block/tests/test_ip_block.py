import pytest

from cc_calc.autonomous_system_number import ASN
from cc_calc.country_code import Alpha2Code
from cc_calc.ip_block._ip_block import IPBlock
from cc_calc.ip_prefix import IPPrefix


@pytest.fixture
def ip_block() -> IPBlock:
    return IPBlock(IPPrefix("192.0.2.0/24"))


def test_block_hash_is_equal_to_prefix_hash(ip_block: IPBlock) -> None:
    prefix_hash = hash(IPPrefix("192.0.2.0/24"))
    assert hash(ip_block) == prefix_hash


def test_block_is_equal_to_block_with_the_same_prefix(ip_block: IPBlock) -> None:
    second_block = IPBlock(IPPrefix("192.0.2.0/24"))
    assert ip_block == second_block


def test_block_is_not_equal_to_block_with_different_prefix(ip_block: IPBlock) -> None:
    second_block = IPBlock(IPPrefix("198.51.100.0/24"))
    assert ip_block != second_block


def test_when_block_is_compared_to_non_block_they_are_not_equal(
    ip_block: IPBlock,
) -> None:
    non_block = ""
    assert ip_block != non_block


@pytest.mark.parametrize(
    "block,expected_len",
    [
        (IPBlock(IPPrefix("192.0.2.0/24")), 2**8),
        (IPBlock(IPPrefix("198.0.0.8/32")), 2**0),
    ],
)
def test_len_is_the_number_of_ip_addresses_in_the_block(
    block: IPBlock, expected_len: int
) -> None:
    assert len(block) == expected_len


def test_when_block_is_created_country_is_set_to_none(ip_block: IPBlock) -> None:
    assert ip_block.country is None


def test_when_block_country_is_set_country_is_updated(ip_block: IPBlock) -> None:
    ip_block.country = Alpha2Code("US")
    assert ip_block.country == Alpha2Code("US")


def test_when_block_is_created_as_is_set_to_none(ip_block: IPBlock) -> None:
    assert ip_block.autonomous_system is None


def test_when_block_as_is_set_as_is_updated(ip_block: IPBlock) -> None:
    ip_block.autonomous_system = ASN(65536)
    assert ip_block.autonomous_system == ASN(65536)
