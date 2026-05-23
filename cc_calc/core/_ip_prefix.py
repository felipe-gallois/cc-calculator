from ipaddress import IPv4Network, IPv6Network


class IPPrefixFormatError(Exception):
    def __init__(self, input: str) -> None:
        self.input = input
        super().__init__(f"expected IPv4 or IPv6, got {input}")


class IPPrefixLoadingError(Exception):
    def __init__(self) -> None:
        super().__init__("could not read from IP prefix database")


class IPPrefix:
    def __init__(self, prefix_str: str) -> None:
        self._prefix: IPv4Network | IPv6Network

        try:
            self._prefix = IPv4Network(prefix_str)
        except Exception:
            try:
                self._prefix = IPv6Network(prefix_str)
            except Exception:
                raise IPPrefixFormatError(prefix_str)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, IPPrefix):
            return NotImplemented

        return self._prefix == other._prefix

    def __hash__(self) -> int:
        return hash(self._prefix)

    def __repr__(self) -> str:
        return f"IPPrefix('{str(self._prefix)}')"

    def __str__(self) -> str:
        return str(self._prefix)

    @property
    def address_part(self) -> str:
        return str(self._prefix.network_address)

    @property
    def n_bits(self) -> int:
        return self._prefix.prefixlen
