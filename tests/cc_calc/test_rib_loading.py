from io import StringIO
from ipaddress import IPv4Network, IPv6Network

from cc_calc.rib_loading import CaidaRIBLoader

IPV4_ENTRY = "xxxx/xxx00|0 123|1234|12345 123.123.123.0/24 i 234.234.234.234\n"

IPV6_ENTRY = "xxxx/xxx00|0 123|1234|12345 2001:db8::/32 i 234.234.234.234\n"


class TestGenerateRIBEntry:
    def test_ipv4_input_returns_entry_with_correct_prefix(self) -> None:
        entry = CaidaRIBLoader._parse_entry(IPV4_ENTRY)

        assert entry.prefix == IPv4Network("123.123.123.0/24")

    def test_ipv6_input_returns_entry_with_correct_prefix(self) -> None:
        entry = CaidaRIBLoader._parse_entry(IPV6_ENTRY)

        assert entry.prefix == IPv6Network("2001:db8::/32")

    def test_valid_input_returns_entry_with_correct_as_path(self) -> None:
        entry = CaidaRIBLoader._parse_entry(IPV4_ENTRY)

        assert entry.as_path == ["123", "1234", "12345"]
