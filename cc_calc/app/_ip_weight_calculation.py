import logging
from collections.abc import Collection

from cc_calc.core import IPBlock

logger = logging.getLogger(__name__)


def calculate_ip_weight(
    src_blocks: Collection[IPBlock], dst_blocks: Collection[IPBlock]
) -> int:
    ip_weight = sum([len(block) for block in src_blocks]) * sum(
        [len(block) for block in dst_blocks]
    )

    logger.info("Calculated IP weight of path")

    return ip_weight
