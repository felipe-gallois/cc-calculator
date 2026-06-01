import gzip
import zlib

import pytest
from pytest_mock import MockerFixture

from cc_calc.db._routeviews_prefix_to_as_db import RouteViewsPrefixToASDB
from cc_calc.repo import InvalidDBDataFormat, UnreachableDB


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


def test_when_file_line_is_malformed_it_skips_the_line(mocker: MockerFixture) -> None:
    mock_open = mocker.mock_open(read_data=("192.0.2.0\t\n"))

    mocker.patch(
        "cc_calc.db._routeviews_prefix_to_as_db.gzip.open",
        return_value=mock_open.return_value,
    )

    prefix_source = RouteViewsPrefixToASDB("")

    it = prefix_source.load_all_ip_prefixes()

    assert list(it) == []


@pytest.mark.parametrize("exception", [FileNotFoundError, PermissionError])
def test_when_gzip_cannot_reach_data_raises_exception(
    mocker: MockerFixture, exception: Exception
) -> None:
    mocker.patch(
        "cc_calc.db._routeviews_prefix_to_as_db.gzip.open",
        side_effect=exception,
    )

    db = RouteViewsPrefixToASDB("")

    with pytest.raises(UnreachableDB):
        next(db.load_all_ip_prefixes())


@pytest.mark.parametrize(
    "exception",
    [
        gzip.BadGzipFile,
        EOFError,
        zlib.error,
        UnicodeDecodeError("utf-8", b"", 0, 1, "boom"),
    ],
)
def test_when_gzip_raises_exception_it_wraps_the_exception(
    mocker: MockerFixture, exception: Exception
) -> None:
    mocker.patch(
        "cc_calc.db._routeviews_prefix_to_as_db.gzip.open",
        side_effect=exception,
    )

    db = RouteViewsPrefixToASDB("")

    with pytest.raises(InvalidDBDataFormat):
        next(db.load_all_ip_prefixes())
