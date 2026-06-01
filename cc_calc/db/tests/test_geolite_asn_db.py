from types import SimpleNamespace

import pytest
from geoip2.errors import AddressNotFoundError
from maxminddb import InvalidDatabaseError
from pytest_mock import MockerFixture

from cc_calc.db._geolite_asn_db import GeoLiteASNDB
from cc_calc.repo import ASNDTO, InvalidDBDataFormat, UnreachableDB


@pytest.mark.parametrize("expected_asn", [65536, 65537])
def test_when_reader_returns_asn_it_returns_dto(
    mocker: MockerFixture,
    expected_asn: ASNDTO,
) -> None:
    mock_reader_cls = mocker.patch("cc_calc.db._geolite_asn_db.Reader")
    mock_reader = mock_reader_cls.return_value.__enter__.return_value

    mock_reader.asn.return_value = SimpleNamespace(
        autonomous_system_number=expected_asn
    )

    db = GeoLiteASNDB("")

    asn = db.load_prefix_asn("192.0.2.0/24")

    assert asn == expected_asn


def test_when_reader_does_not_find_asn_it_returns_none(
    mocker: MockerFixture,
) -> None:
    mock_reader_cls = mocker.patch("cc_calc.db._geolite_asn_db.Reader")
    mock_reader = mock_reader_cls.return_value.__enter__.return_value

    mock_reader.asn.side_effect = AddressNotFoundError("", "")

    db = GeoLiteASNDB("")

    asn = db.load_prefix_asn("192.0.2.0/24")

    assert asn is None


@pytest.mark.parametrize("exception", [FileNotFoundError, PermissionError])
def test_when_reader_cannot_read_content_it_raises_exception(
    mocker: MockerFixture, exception: Exception
) -> None:
    mocker.patch(
        "cc_calc.db._geolite_asn_db.Reader",
        side_effect=exception,
    )

    db = GeoLiteASNDB("")

    with pytest.raises(UnreachableDB):
        db.load_prefix_asn("192.0.2.0/24")


@pytest.mark.parametrize("exception", [InvalidDatabaseError])
def test_when_reader_cannot_parse_content_it_raises_exception(
    mocker: MockerFixture, exception: Exception
) -> None:
    mocker.patch(
        "cc_calc.db._geolite_asn_db.Reader",
        side_effect=exception,
    )

    db = GeoLiteASNDB("")

    with pytest.raises(InvalidDBDataFormat):
        db.load_prefix_asn("192.0.2.0/24")


@pytest.mark.parametrize("exception", [ValueError])
def test_when_reader_takes_invalid_argument_it_raises_exception(
    mocker: MockerFixture, exception: Exception
) -> None:
    mocker.patch(
        "cc_calc.db._geolite_asn_db.Reader",
        side_effect=exception,
    )

    db = GeoLiteASNDB("")

    with pytest.raises(ValueError):
        db.load_prefix_asn("192.0.2.0")
