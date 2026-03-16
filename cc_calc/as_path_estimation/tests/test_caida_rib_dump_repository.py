from io import StringIO

from cc_calc.as_path_estimation._as_path import ASPath
from cc_calc.as_path_estimation._caida_rib_dump_repository import _collect_prefix_paths
from cc_calc.autonomous_system import AS
from cc_calc.ip_prefix import IPPrefix


def test_when_no_entry_matches_prefixes_returns_empty_mapping() -> None:
    text = StringIO("xxxx/xxx00|0 123|1234|12345 123.123.123.0/24 i 234.234.234.234\n")
    prefixes = {IPPrefix("124.124.124.0/24")}

    prefix_path_mappings = _collect_prefix_paths(text, prefixes)

    expected_mapping: dict[IPPrefix, set[ASPath]] = {
        IPPrefix("124.124.124.0/24"): set()
    }

    assert prefix_path_mappings == expected_mapping


def test_when_matches_single_entry_returns_single_mapping() -> None:
    text = StringIO("xxxx/xxx00|0 123|1234|12345 123.123.123.0/24 i 234.234.234.234\n")
    prefixes = {IPPrefix("123.123.123.0/24")}

    prefix_path_mappings = _collect_prefix_paths(text, prefixes)

    expected_mapping = {
        IPPrefix("123.123.123.0/24"): {ASPath((AS(123), AS(1234), AS(12345)))}
    }

    assert prefix_path_mappings == expected_mapping


def test_when_matches_one_of_two_entries_returns_one_mapping() -> None:
    text = StringIO(
        "xxxx/xxx00|0 123|1234|12345 123.123.123.0/24 i 234.234.234.234\n"
        "xxxx/xxx00|0 234|2345|23456 123.111.123.0/24 i 234.234.234.234\n"
    )
    prefixes = {IPPrefix("123.123.123.0/24")}

    prefix_path_mappings = _collect_prefix_paths(text, prefixes)

    expected_mappings = {
        IPPrefix("123.123.123.0/24"): {ASPath((AS(123), AS(1234), AS(12345)))}
    }

    assert prefix_path_mappings == expected_mappings


def test_when_matches_two_entries_with_single_prefix_returns_one_mapping() -> None:
    text = StringIO(
        "xxxx/xxx00|0 123|1234|12345 123.123.123.0/24 i 234.234.234.234\n"
        "xxxx/xxx00|0 234|2345|23456 123.123.123.0/24 i 234.234.234.234\n"
    )
    prefixes = {IPPrefix("123.123.123.0/24")}

    prefix_path_mappings = _collect_prefix_paths(text, prefixes)

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
    prefixes = {IPPrefix("123.123.123.0/24"), IPPrefix("123.111.123.0/24")}

    prefix_path_mappings = _collect_prefix_paths(text, prefixes)

    expected_mappings = {
        IPPrefix("123.123.123.0/24"): {ASPath((AS(123), AS(1234), AS(12345)))},
        IPPrefix("123.111.123.0/24"): {ASPath((AS(234), AS(2345), AS(23456)))},
    }

    assert prefix_path_mappings == expected_mappings
