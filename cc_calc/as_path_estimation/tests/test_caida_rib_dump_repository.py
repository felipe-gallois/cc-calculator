from io import StringIO

import pytest

from cc_calc.as_path_estimation._as_path import ASPath
from cc_calc.as_path_estimation._caida_rib_dump_repository import _collect_prefix_paths
from cc_calc.autonomous_system import AS
from cc_calc.ip_prefix import IPPrefix


@pytest.mark.parametrize("input", ["", "\n", "# commented"])
def test_when_no_entry_returns_empty_mapping(input: str) -> None:
    text = StringIO(input)

    prefix_path_mappings = _collect_prefix_paths(text)

    assert len(prefix_path_mappings) == 0


def test_when_matches_single_entry_returns_single_mapping() -> None:
    text = StringIO("xxxx/xxx00|0 123|1234|12345 123.123.123.0/24 i 234.234.234.234\n")

    prefix_path_mappings = _collect_prefix_paths(text)

    expected_mapping = {
        IPPrefix("123.123.123.0/24"): {ASPath((AS(123), AS(1234), AS(12345)))}
    }

    assert prefix_path_mappings == expected_mapping


def test_when_matches_two_entries_with_single_prefix_returns_one_mapping() -> None:
    text = StringIO(
        "xxxx/xxx00|0 123|1234|12345 123.123.123.0/24 i 234.234.234.234\n"
        "xxxx/xxx00|0 234|2345|23456 123.123.123.0/24 i 234.234.234.234\n"
    )

    prefix_path_mappings = _collect_prefix_paths(text)

    expected_mapping = {
        IPPrefix("123.123.123.0/24"): {
            ASPath((AS(123), AS(1234), AS(12345))),
            ASPath((AS(234), AS(2345), AS(23456))),
        }
    }

    assert prefix_path_mappings == expected_mapping


def test_when_matches_two_entries_with_two_prefixes_returns_two_mappings() -> None:
    text = StringIO(
        "xxxx/xxx00|0 123|1234|12345 123.123.123.0/24 i 234.234.234.234\n"
        "xxxx/xxx00|0 234|2345|23456 123.111.123.0/24 i 234.234.234.234\n"
    )

    prefix_path_mappings = _collect_prefix_paths(text)

    expected_mappings = {
        IPPrefix("123.123.123.0/24"): {ASPath((AS(123), AS(1234), AS(12345)))},
        IPPrefix("123.111.123.0/24"): {ASPath((AS(234), AS(2345), AS(23456)))},
    }

    assert prefix_path_mappings == expected_mappings
