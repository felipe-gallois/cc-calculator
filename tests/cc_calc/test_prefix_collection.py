from io import StringIO
from ipaddress import IPv4Network

import pytest

from cc_calc.prefix_collection import IPv4Collector


REGULAR_IPV4_INPUT = (
    "ripe/rrc00|5 20205|6939|376 132.219.153.0/24 i 64.246.96.5\n"
)

INVALID_IPV4_INPUT = (
    "ripe/rrc00|5 20205|6939|376 132.919.153.0/24 i 64.246.96.5\n"
)

REGULAR_MULTILINE_IPV4_INPUT = (
    "ripe/rrc00|5 20205|6939|376 132.219.153.0/24 i 64.246.96.5\n"
    "ripe/rrc01|5 20204|6929|375 132.219.153.0/24 i 65.236.96.7\n"
)

REGULAR_IPV4_PREFIX = IPv4Network("132.219.153.0/24")


def test_create_ipv4collector():
    src = StringIO()
    IPv4Collector(src)


def test_ipv4collector_find_no_ip():
    src = StringIO()
    collector = IPv4Collector(src)

    prefixes = collector.collect_prefixes()

    assert len(prefixes) == 0


def test_ipv4collector_find_one_ip():
    src = StringIO(REGULAR_IPV4_INPUT)
    collector = IPv4Collector(src)

    prefixes = collector.collect_prefixes()

    assert len(prefixes) == 1


def test_ipv4collector_list_one_ip():
    src = StringIO(REGULAR_IPV4_INPUT)
    collector = IPv4Collector(src)

    prefixes = collector.collect_prefixes()

    assert REGULAR_IPV4_PREFIX in prefixes


def test_ipv4collector_ignore_trailing_new_line():
    src = StringIO("\n")
    collector = IPv4Collector(src)

    prefixes = collector.collect_prefixes()

    assert len(prefixes) == 0


def test_ipv4collector_same_prefix_return_once():
    src = StringIO(REGULAR_MULTILINE_IPV4_INPUT)
    collector = IPv4Collector(src)

    prefixes = collector.collect_prefixes()

    assert REGULAR_IPV4_PREFIX in prefixes


def test_ipv4collector_raise_invalid_prefix():
    src = StringIO(INVALID_IPV4_INPUT)
    collector = IPv4Collector(src)

    with pytest.raises(ValueError):
        collector.collect_prefixes()
