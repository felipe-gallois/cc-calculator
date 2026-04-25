from collections.abc import Collection

from cc_calc.ip_block import IPBlock


def calculate_ip_weight(
    src_blocks: Collection[IPBlock], dst_blocks: Collection[IPBlock]
) -> int:
    return sum([len(block) for block in src_blocks]) * sum(
        [len(block) for block in dst_blocks]
    )
