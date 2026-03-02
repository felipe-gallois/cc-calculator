import ipaddress as ipaddr


class IPAddressError(Exception):
    pass


class IPv4Address:
    def __init__(self, address_str: str) -> None:
        try:
            self._address = ipaddr.IPv4Address(address_str)
        except Exception as e:
            raise IPAddressError(f"{address_str} is not a valid IPv4 address") from e

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, IPv4Address):
            return NotImplemented

        return self._address == other._address

    def __hash__(self) -> int:
        return hash(self._address)

    def __repr__(self) -> str:
        return f"IPv4Address('{str(self._address)}')"

    def __str__(self) -> str:
        return str(self._address)
