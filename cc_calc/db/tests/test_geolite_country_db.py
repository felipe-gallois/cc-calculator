from types import SimpleNamespace

import pytest
from geoip2.errors import AddressNotFoundError
from maxminddb import InvalidDatabaseError
from pytest_mock import MockerFixture

from cc_calc.db._geolite_country_db import GeoLiteCountryDB
from cc_calc.repo import (
    CountryDTO,
    InvalidDBDataFormat,
    UnreachableDB,
)


@pytest.mark.parametrize("expected_country", ["BR", "US"])
def test_when_reader_returns_asn_returns_dto(
    mocker: MockerFixture,
    expected_country: CountryDTO,
) -> None:
    mock_reader_cls = mocker.patch("cc_calc.db._geolite_country_db.Reader")
    mock_reader = mock_reader_cls.return_value.__enter__.return_value

    mock_reader.country.return_value = SimpleNamespace(
        country=SimpleNamespace(iso_code=expected_country)
    )

    db = GeoLiteCountryDB("")

    country = db.load_prefix_country("192.0.2.0/24")

    assert country == expected_country


def test_when_reader_does_not_find_country_returns_none(
    mocker: MockerFixture,
) -> None:
    mock_reader_cls = mocker.patch("cc_calc.db._geolite_country_db.Reader")
    mock_reader = mock_reader_cls.return_value.__enter__.return_value

    mock_reader.country.side_effect = AddressNotFoundError("", "")

    db = GeoLiteCountryDB("")

    country = db.load_prefix_country("192.0.2.0/24")

    assert country is None


@pytest.mark.parametrize("exception", [FileNotFoundError, PermissionError])
def test_when_reader_cannot_read_content_it_raises_exception(
    mocker: MockerFixture, exception: Exception
) -> None:
    mocker.patch(
        "cc_calc.db._geolite_country_db.Reader",
        side_effect=exception,
    )

    db = GeoLiteCountryDB("")

    with pytest.raises(UnreachableDB):
        db.load_prefix_country("192.0.2.0/24")


@pytest.mark.parametrize("exception", [InvalidDatabaseError])
def test_when_reader_cannot_parse_content_it_raises_exception(
    mocker: MockerFixture, exception: Exception
) -> None:
    mocker.patch(
        "cc_calc.db._geolite_country_db.Reader",
        side_effect=exception,
    )

    db = GeoLiteCountryDB("")

    with pytest.raises(InvalidDBDataFormat):
        db.load_prefix_country("192.0.2.0/24")


@pytest.mark.parametrize("exception", [ValueError])
def test_when_reader_takes_invalid_argument_it_raises_exception(
    mocker: MockerFixture, exception: Exception
) -> None:
    mocker.patch(
        "cc_calc.db._geolite_country_db.Reader",
        side_effect=exception,
    )

    db = GeoLiteCountryDB("")

    with pytest.raises(ValueError):
        db.load_prefix_country("192.0.2.0")
