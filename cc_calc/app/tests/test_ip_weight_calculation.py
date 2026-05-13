import pytest

from cc_calc.app._ip_weight_calculation import calculate_ip_weight
from cc_calc.core import IPBlock, IPPrefix


@pytest.mark.parametrize(
    "src_blocks,dst_blocks",
    [
        (set(), {IPBlock(IPPrefix("192.0.2.0/24"))}),
        ({IPBlock(IPPrefix("192.0.2.0/24"))}, set()),
    ],
)
def test_when_block_list_is_empty_return_weight_zero(
    src_blocks: set[IPBlock], dst_blocks: set[IPBlock]
) -> None:
    ip_weight = calculate_ip_weight(src_blocks, dst_blocks)
    assert ip_weight == 0


@pytest.mark.parametrize(
    "src_blocks,dst_blocks,expected_weight",
    [
        (
            {IPBlock(IPPrefix("192.0.2.0/24"))},
            {IPBlock(IPPrefix("198.51.100.0/24"))},
            2**8 * 2**8,
        ),
        (
            {IPBlock(IPPrefix("192.0.2.0/24"))},
            {IPBlock(IPPrefix("198.0.0.8/32"))},
            2**8 * 2**0,
        ),
        (
            {IPBlock(IPPrefix("192.0.2.0/24")), IPBlock(IPPrefix("198.0.0.8/32"))},
            {IPBlock(IPPrefix("203.0.113.0/24"))},
            (2**8 + 2**0) * 2**8,
        ),
    ],
)
def test_when_each_block_list_has_blocks_return_product_of_sum_of_weights(
    src_blocks: set[IPBlock], dst_blocks: set[IPBlock], expected_weight: int
) -> None:
    ip_weight = calculate_ip_weight(src_blocks, dst_blocks)
    assert ip_weight == expected_weight
