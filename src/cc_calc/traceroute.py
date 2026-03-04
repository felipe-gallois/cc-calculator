from collections import Counter
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
        return [
            idx for idx in range(1, len(self)) if self[idx]._as != self[idx - 1]._as
        ]


class AnnotatedTracerouteList:
    def __init__(self) -> None:
        self._ingress_map: dict[
            tuple[IPv4Address, AS], Counter[tuple[CountryPath, IPv4Address]]
        ] = dict()

        self._as_country_map: dict[
            tuple[AS, Country, AS], Counter[tuple[CountryPath, IPv4Address]]
        ] = dict()

        self._as_map: dict[tuple[AS, AS], Counter[tuple[CountryPath, IPv4Address]]] = (
            dict()
        )

        self._country_map: dict[
            tuple[Country, AS], Counter[tuple[CountryPath, IPv4Address]]
        ] = dict()

        self._default_map: dict[AS, Counter[tuple[CountryPath, IPv4Address]]] = dict()

    def path_from_ingress(
        self, ingress: IPv4Address, dst_as: AS
    ) -> tuple[CountryPath | None, IPv4Address | None]:
        return self._get_map_entry(self._ingress_map, (ingress, dst_as))

    def path_from_as_and_country(
        self, src_as: AS, country: Country, dst_as: AS
    ) -> tuple[CountryPath | None, IPv4Address | None]:
        return self._get_map_entry(self._as_country_map, (src_as, country, dst_as))

    def path_from_as(
        self, src_as: AS, dst_as: AS
    ) -> tuple[CountryPath | None, IPv4Address | None]:
        return self._get_map_entry(self._as_map, (src_as, dst_as))

    def path_from_country(
        self, country: Country, dst_as: AS
    ) -> tuple[CountryPath | None, IPv4Address | None]:
        return self._get_map_entry(self._country_map, (country, dst_as))

    def path_to_as(self, dst_as: AS) -> tuple[CountryPath | None, IPv4Address | None]:
        return self._get_map_entry(self._default_map, dst_as)

    def add_annotated_traceroute(self, trace: AnnotatedTraceroute) -> None:
        self._add_traceroute_to_ingress_map(trace)
        self._add_traceroute_to_as_and_country_maps(trace)
        self._add_traceroute_to_default_map(trace)

    def _add_traceroute_to_ingress_map(self, trace: AnnotatedTraceroute) -> None:
        ingress_indices = trace.ingress_indices

        for ingress_idx, next_ingress_idx in zip(ingress_indices, ingress_indices[1:]):
            ingress = trace[ingress_idx]
            next_ingress = trace[next_ingress_idx]

            key = (ingress.address, next_ingress._as)
            value = (
                CountryPath(
                    [hop.country for hop in trace[ingress_idx : next_ingress_idx + 1]]
                ),
                next_ingress.address,
            )

            self._add_map_entry(self._ingress_map, key, value)

    def _add_traceroute_to_as_and_country_maps(
        self, trace: AnnotatedTraceroute
    ) -> None:
        ingress_indices = trace.ingress_indices
        egress_indices = map(lambda x: x - 1, ingress_indices)

        for egress_idx, next_ingress_idx in zip(egress_indices, ingress_indices):
            egress = trace[egress_idx]
            next_ingress = trace[next_ingress_idx]

            value = (
                CountryPath(
                    [hop.country for hop in trace[egress_idx : next_ingress_idx + 1]]
                ),
                next_ingress.address,
            )

            self._add_map_entry(self._as_map, (egress._as, next_ingress._as), value)

            self._add_map_entry(
                self._country_map, (egress.country, next_ingress._as), value
            )

            self._add_map_entry(
                self._as_country_map,
                (egress._as, egress.country, next_ingress._as),
                value,
            )

    def _add_traceroute_to_default_map(self, trace: AnnotatedTraceroute) -> None:
        for ingress_idx in trace.ingress_indices:
            ingress = trace[ingress_idx]

            key = ingress._as
            value = (CountryPath([ingress.country]), ingress.address)

            self._add_map_entry(self._default_map, key, value)

    def _get_map_entry[T](
        self, map: dict[T, Counter[tuple[CountryPath, IPv4Address]]], key: T
    ) -> tuple[CountryPath | None, IPv4Address | None]:
        try:
            counter = map[key]
            path, new_ingress = counter.most_common(1)[0][0]
            return path, new_ingress
        except (KeyError, IndexError):
            return None, None

    def _add_map_entry[S, T](self, map: dict[S, Counter[T]], key: S, value: T) -> None:
        try:
            counter = map[key]
        except KeyError:
            counter = Counter()
            map[key] = counter
        finally:
            counter[value] += 1
