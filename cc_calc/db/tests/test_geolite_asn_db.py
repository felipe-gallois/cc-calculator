from types import SimpleNamespace

import pytest
from geoip2.errors import AddressNotFoundError
from pytest_mock import MockerFixture

from cc_calc.db._geolite_asn_db import GeoLiteASNDB
from cc_calc.repo._ip_block_repo import (
    ASNDTO,
    IPBlockLoadingError,
)


def test_when_reader_raises_exception_it_wraps_the_exception(
    mocker: MockerFixture,
) -> None:
    mocker.patch(
        "cc_calc.db._geolite_asn_db.Reader",
        side_effect=FileNotFoundError,
    )

    db = GeoLiteASNDB("")

    with pytest.raises(IPBlockLoadingError):
        db.load_prefix_asn("192.0.2.0/24")


def test_when_reader_does_not_find_asn_returns_none(
    mocker: MockerFixture,
) -> None:
    mock_reader_cls = mocker.patch("cc_calc.db._geolite_asn_db.Reader")
    mock_reader = mock_reader_cls.return_value.__enter__.return_value

    mock_reader.asn.side_effect = AddressNotFoundError("", "")

    db = GeoLiteASNDB("")

    asn = db.load_prefix_asn("192.0.2.0/24")

    assert asn is None


@pytest.mark.parametrize("expected_asn", [65536, 65537])
def test_when_reader_returns_asn_returns_dto(
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
