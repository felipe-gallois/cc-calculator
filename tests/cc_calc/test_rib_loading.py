from io import StringIO

from cc_calc.bgp_simulation import ASPath, ip_prefix
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

SINGLE_ENTRY_PATH = {"123.123.123.0/24": [["123", "1234", "12345"]]}

DIFFERENT_PREFIX_ENTRIES_PATHS = {
    "123.123.123.0/24": [["123", "1234", "12345"]],
    "123.111.123.0/24": [["234", "2345", "23456"]],
}

SAME_PREFIX_ENTRIES_PATHS = {
    "123.123.123.0/24": [["123", "1234", "12345"], ["234", "2345", "23456"]],
}


class TestLoadPrefixPaths:
    def test_when_receives_single_entry_returns_single_mapping(self) -> None:
        text = StringIO(SINGLE_ENTRY)

        prefix_path_mappings = CaidaRIBLoader._parse_entries(text)

        expected_mapping = {
            ip_prefix(key): list(map(ASPath, values))
            for key, values in SINGLE_ENTRY_PATH.items()
        }

        assert prefix_path_mappings == expected_mapping

    def test_when_receives_entries_with_two_different_prefixes_returns_two_mappings(
        self,
    ) -> None:
        text = StringIO(DIFFERENT_PREFIX_ENTRIES)

        prefix_path_mappings = CaidaRIBLoader._parse_entries(text)

        expected_mappings = {
            ip_prefix(key): list(map(ASPath, values))
            for key, values in DIFFERENT_PREFIX_ENTRIES_PATHS.items()
        }

        assert prefix_path_mappings == expected_mappings

    def test_when_receives_entries_with_two_equal_prefixes_returns_one_mapping(
        self,
    ) -> None:
        text = StringIO(SAME_PREFIX_ENTRIES)

        prefix_path_mappings = CaidaRIBLoader._parse_entries(text)

        expected_mapping = {
            ip_prefix(key): list(map(ASPath, values))
            for key, values in SAME_PREFIX_ENTRIES_PATHS.items()
        }

        assert prefix_path_mappings == expected_mapping
