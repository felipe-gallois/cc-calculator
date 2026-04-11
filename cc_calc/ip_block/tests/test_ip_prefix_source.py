from pytest_mock import MockerFixture

from cc_calc.ip_block._ip_prefix_source import RouteViewsIPPrefixSource


def test_when_file_has_one_prefix_loads_prefix(mocker: MockerFixture) -> None:
    mock_open = mocker.mock_open(read_data="192.0.2.0\t24\t65536\n")

    mocker.patch(
        "cc_calc.ip_block._ip_prefix_source.gzip.open",
        return_value=mock_open.return_value,
    )

    prefix_source = RouteViewsIPPrefixSource("")
    prefixes = prefix_source.load_all_ip_prefixes()

    assert prefixes == {"192.0.2.0/24"}


def test_when_file_has_two_prefixes_loads_both_prefixes(mocker: MockerFixture) -> None:
    mock_open = mocker.mock_open(
        read_data=("192.0.2.0\t24\t65536\n198.51.100.0\t24\t65536\n")
    )

    mocker.patch(
        "cc_calc.ip_block._ip_prefix_source.gzip.open",
        return_value=mock_open.return_value,
    )

    prefix_source = RouteViewsIPPrefixSource("")
    prefixes = prefix_source.load_all_ip_prefixes()

    assert prefixes == {"192.0.2.0/24", "198.51.100.0/24"}
