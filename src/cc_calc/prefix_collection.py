import re

from io import TextIOBase
from ipaddress import IPv4Network


class IPv4Collector:
    def __init__(self, source: TextIOBase):
        self.source = source

    def collect_prefixes(self) -> set[IPv4Network]:
        prefixes = set()

        for line in self.source:
            prefix_str = re.search(r"(?:\d{1,3}\.){3}\d{1,3}/\d{1,2}", line)

            if prefix_str:
                prefix = IPv4Network(prefix_str.group(0))
                prefixes.add(prefix)

        return prefixes
