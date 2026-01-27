from io import StringIO
from ipaddress import IPv4Network

import pytest

from cc_calc.prefix_collection import _collect_prefixes

REGULAR_IPV4_INPUT = "ripe/rrc00|5 20205|6939|376 132.219.153.0/24 i 64.246.96.5\n"

INVALID_IPV4_INPUT = "ripe/rrc00|5 20205|6939|376 132.919.153.0/24 i 64.246.96.5\n"

REGULAR_MULTILINE_IPV4_INPUT = (
    "ripe/rrc00|5 20205|6939|376 132.219.153.0/24 i 64.246.96.5\n"
    "ripe/rrc01|5 20204|6929|375 132.219.153.0/24 i 65.236.96.7\n"
)

REGULAR_IPV4_PREFIX = IPv4Network("132.219.153.0/24")


class TestCollectCompressedPrefixes:
    @pytest.mark.parametrize("content", ["", "\n"])
    def test_returns_empty_for_empty_input(self, content: str) -> None:
        src = StringIO(content)

        prefixes = _collect_prefixes(src)

        assert not prefixes

    def test_returns_single_prefix_for_valid_input(self) -> None:
        src = StringIO(REGULAR_IPV4_INPUT)

        prefixes = _collect_prefixes(src)

        assert prefixes == {REGULAR_IPV4_PREFIX}

    def test_return_unique_prefixes_for_repeated_entries(self) -> None:
        src = StringIO(REGULAR_MULTILINE_IPV4_INPUT)

        prefixes = _collect_prefixes(src)

        assert REGULAR_IPV4_PREFIX in prefixes

    def test_raises_error_for_invalid_prefix(self) -> None:
        src = StringIO(INVALID_IPV4_INPUT)

        with pytest.raises(ValueError):
            _collect_prefixes(src)
