from io import StringIO

from cc_calc.bgp_simulation import IPPrefix
from cc_calc.rib_loading import CaidaRIBLoader

SINGLE_ENTRY = "xxxx/xxx00|0 123|1234|12345 123.123.123.0/24 i 234.234.234.234\n"

DIFFERENT_PREFIX_ENTRIES = (
    "xxxx/xxx00|0 123|1234|12345 123.123.123.0/24 i 234.234.234.234\n"
    "xxxx/xxx00|0 234|2345|23456 123.111.123.0/24 i 234.234.234.234\n"
)

SAME_PREFIX_ENTRIES = (
    "xxxx/xxx00|0 123|1234|12345 123.123.123.0/24 i 234.234.234.234\n"
    "xxxx/xxx00|0 234|2345|23456 123.123.123.0/24 i 234.234.234.234\n"
)

SINGLE_ENTRY_PATH = {IPPrefix("123.123.123.0/24"): [["123", "1234", "12345"]]}

DIFFERENT_PREFIX_ENTRIES_PATHS = {
    IPPrefix("123.123.123.0/24"): [["123", "1234", "12345"]],
    IPPrefix("123.111.123.0/24"): [["234", "2345", "23456"]],
}

SAME_PREFIX_ENTRIES_PATHS = {
    IPPrefix("123.123.123.0/24"): [["123", "1234", "12345"], ["234", "2345", "23456"]],
}


class TestLoadPrefixPaths:
    def test_when_receives_single_entry_returns_single_mapping(self) -> None:
        text = StringIO(SINGLE_ENTRY)

        prefix_paths = CaidaRIBLoader._parse_entries(text)

        assert prefix_paths == SINGLE_ENTRY_PATH

    def test_when_receives_entries_with_two_different_prefixes_returns_two_mappings(
        self,
    ) -> None:
        text = StringIO(DIFFERENT_PREFIX_ENTRIES)

        prefix_paths = CaidaRIBLoader._parse_entries(text)

        assert prefix_paths == DIFFERENT_PREFIX_ENTRIES_PATHS

    def test_when_receives_entries_with_two_equal_prefixes_returns_one_mapping(
        self,
    ) -> None:
        text = StringIO(DIFFERENT_PREFIX_ENTRIES)

        prefix_paths = CaidaRIBLoader._parse_entries(text)

        assert prefix_paths == DIFFERENT_PREFIX_ENTRIES_PATHS
