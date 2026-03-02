from collections.abc import Iterator
from dataclasses import dataclass
from typing import overload

from cc_calc.autonomous_system import AS
from cc_calc.country import Country, CountryPath
from cc_calc.ip_address import IPv4Address


@dataclass(frozen=True)
class AnnotatedIPAddress:
    address: IPv4Address
    _as: AS
    country: Country


class AnnotatedTracerouteError(Exception):
    pass


class AnnotatedTraceroute:
    def __init__(self, trace: list[AnnotatedIPAddress]) -> None:
        self._trace = trace

    def __len__(self) -> int:
        return len(self._trace)

    def __iter__(self) -> Iterator[AnnotatedIPAddress]:
        for address in self._trace:
            yield address

    @overload
    def __getitem__(self, key: int) -> AnnotatedIPAddress:
        pass

    @overload
    def __getitem__(self, key: slice) -> "AnnotatedTraceroute":
        pass

    def __getitem__(
        self, key: int | slice
    ) -> AnnotatedIPAddress | "AnnotatedTraceroute" | None:
        if isinstance(key, slice):
            return AnnotatedTraceroute(self._trace[key])

        try:
            return self._trace[key]
        except IndexError as e:
            raise AnnotatedTracerouteError(f"Key {key} is invalid") from e

    @property
    def addresses(self) -> list[IPv4Address]:
        return [address.address for address in self._trace]

    @property
    def ases(self) -> list[AS]:
        return [address._as for address in self._trace]

    @property
    def countries(self) -> list[Country]:
        return [address.country for address in self._trace]

    @property
    def ingress_indices(self) -> list[int]:
        return [idx for idx in range(1, len(self)) if self[idx] != self[idx - 1]]


class AnnotatedTracerouteList:
    def __init__(self) -> None:
        self._ingress_map: dict[
            tuple[IPv4Address, AS], tuple[CountryPath, IPv4Address]
        ] = dict()

    def add_annotated_traceroute(self, trace: AnnotatedTraceroute) -> None:
        ingress_indices = trace.ingress_indices

        for i, ingress_idx in enumerate(ingress_indices):
            for new_ingress_idx in ingress_indices[i + 1 :]:
                ingress = trace[ingress_idx]
                new_ingress = trace[new_ingress_idx]
                self._ingress_map[(ingress.address, new_ingress._as)] = (
                    CountryPath(
                        [
                            hop.country
                            for hop in trace[ingress_idx : new_ingress_idx + 1]
                        ]
                    ),
                    new_ingress.address,
                )

    def path_from_ingress(
        self, ingress: IPv4Address, dst_as: AS
    ) -> tuple[CountryPath | None, IPv4Address | None]:
        try:
            path, new_ingress = self._ingress_map[(ingress, dst_as)]
            return path, new_ingress
        except KeyError:
            return None, None
