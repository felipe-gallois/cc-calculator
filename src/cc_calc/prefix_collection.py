import bz2
import re

from typing import BinaryIO, TextIO
from ipaddress import IPv4Network


class IPv4Collector:
    def collect_compressed(self, source: BinaryIO) -> set[IPv4Network]:
        with bz2.open(source, mode="rt", encoding="utf-8") as text:
            return self._collect_prefixes(text)

    def _collect_prefixes(self, source: TextIO) -> set[IPv4Network]:
        prefixes = set()

        for line in source:
            prefix_str = re.search(r"(?:\d{1,3}\.){3}\d{1,3}/\d{1,2}", line)

            if prefix_str:
                prefix = IPv4Network(prefix_str.group(0))
                prefixes.add(prefix)

        return prefixes
