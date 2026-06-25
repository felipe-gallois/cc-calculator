import pytest

from cc_calc.core._as_weight_graph import ASWeightGraph
from cc_calc.core._autonomous_system_number import ASN
from cc_calc.core._country_code import Alpha2Code
from cc_calc.core._ip_block import IPBlock
from cc_calc.core._ip_prefix import IPPrefix


@pytest.fixture
def weight_graph() -> ASWeightGraph:
    return ASWeightGraph()


def test_when_just_created_it_returns_no_weights_for_as(
    weight_graph: ASWeightGraph,
) -> None:
    assert weight_graph.get_as_weights(ASN(65536)) == dict()


@pytest.mark.parametrize(
    "ip_prefix,weight",
    [
        (IPPrefix("192.0.2.0/24"), 2**8),
        (IPPrefix("192.0.2.0/28"), 2**4),
    ],
)
def test_when_one_brazilian_ip_block_is_added_it_returns_block_weight_for_as(
    ip_prefix: IPPrefix,
    weight: int,
    weight_graph: ASWeightGraph,
) -> None:
    weight_graph.add_ip_block(IPBlock(ip_prefix, Alpha2Code("BR"), ASN(65536)))
    assert weight_graph.get_as_weights(ASN(65536)) == {Alpha2Code("BR"): weight}


def test_when_one_american_ip_block_is_added_it_returns_blocks_weight_for_as(
    weight_graph: ASWeightGraph,
) -> None:
    weight_graph.add_ip_block(
        IPBlock(IPPrefix("192.0.2.0/24"), Alpha2Code("US"), ASN(65536))
    )
    assert weight_graph.get_as_weights(ASN(65536)) == {Alpha2Code("US"): 2**8}


@pytest.mark.parametrize(
    "ip_block_as,other_as",
    [
        (ASN(65536), ASN(65537)),
        (ASN(65537), ASN(65538)),
    ],
)
def test_when_one_ip_block_of_as_is_added_it_returns_no_weights_for_another_as(
    ip_block_as: ASN,
    other_as: ASN,
    weight_graph: ASWeightGraph,
) -> None:
    weight_graph.add_ip_block(
        IPBlock(IPPrefix("192.0.2.0/24"), Alpha2Code("BR"), ip_block_as)
    )
    assert weight_graph.get_as_weights(other_as) == dict()


def test_when_two_ip_blocks_of_different_ases_are_added_it_returns_weights_of_each_as(
    weight_graph: ASWeightGraph,
) -> None:
    weight_graph.add_ip_block(
        IPBlock(IPPrefix("192.0.2.0/24"), Alpha2Code("BR"), ASN(65536))
    )
    weight_graph.add_ip_block(
        IPBlock(IPPrefix("198.51.100.0/28"), Alpha2Code("BR"), ASN(65537))
    )
    assert weight_graph.get_as_weights(ASN(65536)) == {Alpha2Code("BR"): 2**8}
    assert weight_graph.get_as_weights(ASN(65537)) == {Alpha2Code("BR"): 2**4}


def test_when_two_ip_blocks_of_same_as_and_country_are_added_it_returns_summed_weight(
    weight_graph: ASWeightGraph,
) -> None:
    weight_graph.add_ip_block(
        IPBlock(IPPrefix("192.0.2.0/24"), Alpha2Code("BR"), ASN(65536))
    )
    weight_graph.add_ip_block(
        IPBlock(IPPrefix("198.51.100.0/28"), Alpha2Code("BR"), ASN(65536))
    )
    assert weight_graph.get_as_weights(ASN(65536)) == {Alpha2Code("BR"): 2**8 + 2**4}


def test_when_two_ip_blocks_of_different_countries_are_added_it_returns_both_weights(
    weight_graph: ASWeightGraph,
) -> None:
    weight_graph.add_ip_block(
        IPBlock(IPPrefix("192.0.2.0/24"), Alpha2Code("BR"), ASN(65536))
    )
    weight_graph.add_ip_block(
        IPBlock(IPPrefix("198.51.100.0/28"), Alpha2Code("US"), ASN(65536))
    )
    assert weight_graph.get_as_weights(ASN(65536)) == {
        Alpha2Code("BR"): 2**8,
        Alpha2Code("US"): 2**4,
    }
