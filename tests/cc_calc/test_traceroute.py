import pytest

from cc_calc.autonomous_system import AS
from cc_calc.country import Country, CountryPath
from cc_calc.ip_address import IPv4Address
from cc_calc.traceroute import (
    AnnotatedIPAddress,
    AnnotatedTraceroute,
    AnnotatedTracerouteList,
)


class TestSearchPathByIngressPoint:
    @pytest.fixture
    def traceroute(self) -> AnnotatedTraceroute:
        annotated_ips = [
            AnnotatedIPAddress(IPv4Address("192.0.2.1"), AS(65536), Country("CA")),
            AnnotatedIPAddress(IPv4Address("192.0.2.2"), AS(65536), Country("CA")),
            AnnotatedIPAddress(IPv4Address("198.51.100.1"), AS(65537), Country("US")),
            AnnotatedIPAddress(IPv4Address("203.0.113.1"), AS(65538), Country("BR")),
            AnnotatedIPAddress(IPv4Address("203.0.113.2"), AS(65539), Country("BR")),
        ]

        return AnnotatedTraceroute(annotated_ips)

    def test_when_no_traceroutes_informed_returns_none(self) -> None:
        ingress = IPv4Address("192.0.2.254")
        dst_as = AS(65540)

        list = AnnotatedTracerouteList()

        path, new_ingress = list.path_from_ingress(ingress, dst_as)

        assert path is None
        assert new_ingress is None

    @pytest.mark.parametrize(
        "ingress, dst_as, expected_path, expected_new_ingress",
        [
            (
                IPv4Address("198.51.100.1"),
                AS(65538),
                CountryPath([Country("US"), Country("BR")]),
                IPv4Address("203.0.113.1"),
            ),
            (
                IPv4Address("203.0.113.1"),
                AS(65539),
                CountryPath([Country("BR")]),
                IPv4Address("203.0.113.2"),
            ),
        ],
    )
    def test_when_traceroute_is_known_returns_path_and_ingress_on_valid_ingress(
        self,
        ingress: IPv4Address,
        dst_as: AS,
        traceroute: AnnotatedTraceroute,
        expected_path: CountryPath,
        expected_new_ingress: IPv4Address,
    ) -> None:
        list = AnnotatedTracerouteList()
        list.add_annotated_traceroute(traceroute)

        path, new_ingress = list.path_from_ingress(ingress, dst_as)

        assert path == expected_path
        assert new_ingress == expected_new_ingress

    def test_when_traceroute_is_known_returns_none_on_invalid_ingress(
        self, traceroute: AnnotatedTraceroute
    ) -> None:
        ingress = IPv4Address("192.0.2.1")
        dst_as = AS(65537)

        list = AnnotatedTracerouteList()
        list.add_annotated_traceroute(traceroute)

        path, new_ingress = list.path_from_ingress(ingress, dst_as)

        assert path is None
        assert new_ingress is None

    def test_when_traceroute_is_known_returns_none_for_previous_as(
        self, traceroute: AnnotatedTraceroute
    ) -> None:
        ingress = IPv4Address("198.51.100.1")
        dst_as = AS(65536)

        list = AnnotatedTracerouteList()
        list.add_annotated_traceroute(traceroute)

        path, new_ingress = list.path_from_ingress(ingress, dst_as)

        assert path is None
        assert new_ingress is None
