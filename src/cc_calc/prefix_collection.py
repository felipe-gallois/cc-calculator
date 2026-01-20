import re

from typing import TextIO
from ipaddress import IPv4Network


class IPv4Collector:
    def _collect_prefixes(self, source: TextIO) -> set[IPv4Network]:
        prefixes = set()

        for line in source:
            prefix_str = re.search(r"(?:\d{1,3}\.){3}\d{1,3}/\d{1,2}", line)

            if prefix_str:
                prefix = IPv4Network(prefix_str.group(0))
                prefixes.add(prefix)

        return prefixes
