import pytest
from pytest_mock import MockerFixture

from cc_calc.db._routeviews_prefix_to_as_db import RouteViewsPrefixToASDB
from cc_calc.repo._ip_block_repo import IPBlockLoadingError


def test_when_gzip_raises_exception_wraps_exception(mocker: MockerFixture) -> None:
    mocker.patch(
        "cc_calc.db._routeviews_prefix_to_as_db.gzip.open",
        side_effect=FileNotFoundError,
    )

    prefix_source = RouteViewsPrefixToASDB("")

    with pytest.raises(IPBlockLoadingError):
        next(prefix_source.load_all_ip_prefixes())


def test_when_file_has_one_prefix_yields_prefix(mocker: MockerFixture) -> None:
    mock_open = mocker.mock_open(read_data="192.0.2.0\t24\t65536\n")

    mocker.patch(
        "cc_calc.db._routeviews_prefix_to_as_db.gzip.open",
        return_value=mock_open.return_value,
    )

    prefix_source = RouteViewsPrefixToASDB("")

    it = prefix_source.load_all_ip_prefixes()

    assert list(it) == ["192.0.2.0/24"]


def test_when_file_has_two_prefixes_yields_both_prefixes(mocker: MockerFixture) -> None:
    mock_open = mocker.mock_open(
        read_data=("192.0.2.0\t24\t65536\n198.51.100.0\t24\t65536\n")
    )

    mocker.patch(
        "cc_calc.db._routeviews_prefix_to_as_db.gzip.open",
        return_value=mock_open.return_value,
    )

    prefix_source = RouteViewsPrefixToASDB("")

    it = prefix_source.load_all_ip_prefixes()

    assert list(it) == ["192.0.2.0/24", "198.51.100.0/24"]
