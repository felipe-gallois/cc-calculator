import gzip
import zlib
from typing import Any
from unittest.mock import mock_open, patch

import pytest

from cc_calc.core import ASN, Alpha2Code, ASRepositoryError
from cc_calc.db._file_as_repository import FileASRepository


@pytest.fixture
def as_repo() -> FileASRepository:
    return FileASRepository("")


@pytest.fixture
def mock_content() -> Any:
    return mock_open(
        read_data=(
            "#\n"
            "# format:org_id|changed|org_name|country|source\n"
            "@aut-65536-ARIN|19700101|Company Inc.|US|ARIN\n"
            "# format:aut|changed|aut_name|org_id|opaque_id|source\n"
            "65536|19700101|COM|@aut-65536-ARIN|1234567_ARIN|ARIN\n"
        )
    )


@pytest.fixture
def mock_content_two() -> Any:
    return mock_open(
        read_data=(
            "#\n"
            "# format:org_id|changed|org_name|country|source\n"
            "@aut-65537-ARIN|19700101|Company Inc.|CA|ARIN\n"
            "# format:aut|changed|aut_name|org_id|opaque_id|source\n"
            "65537|19700101|COM|@aut-65537-ARIN|1234567_ARIN|ARIN\n"
        )
    )


@pytest.fixture
def mock_content_three() -> Any:
    return mock_open(
        read_data=(
            "#\n"
            "# format:org_id|changed|org_name|country|source\n"
            "@aut-65536-ARIN|19700101|Company Inc.|US|ARIN\n"
            "@aut-65537-ARIN|19700101|Company Inc.|CA|ARIN\n"
            "# format:aut|changed|aut_name|org_id|opaque_id|source\n"
            "65536|19700101|COM|@aut-65536-ARIN|1234567_ARIN|ARIN\n"
            "65537|19700101|COM|@aut-65537-ARIN|1234567_ARIN|ARIN\n"
        )
    )


@pytest.mark.parametrize(
    "exception", [FileNotFoundError, gzip.BadGzipFile, EOFError, zlib.error, OSError]
)
def test_when_gzip_raises_exception_propagates_the_exception(
    as_repo: FileASRepository,
    exception: Exception,
) -> None:
    with patch("gzip.open", side_effect=exception):
        with pytest.raises(ASRepositoryError):
            as_repo.load_as(ASN(65536))


def test_when_asn_is_not_in_file_raises_exception(
    as_repo: FileASRepository, mock_content: Any
) -> None:
    with patch("gzip.open", mock_content):
        with pytest.raises(ASRepositoryError):
            as_repo.load_as(ASN(65537))


def test_when_as_registered_in_us_is_in_file_returns_as(
    as_repo: FileASRepository,
    mock_content: Any,
) -> None:
    with patch("gzip.open", mock_content):
        _as = as_repo.load_as(ASN(65536))

    assert _as.asn == ASN(65536)
    assert _as.country_of_registry == Alpha2Code("US")


def test_when_as_registered_in_ca_is_in_file_returns_as(
    as_repo: FileASRepository,
    mock_content_two: Any,
) -> None:
    with patch("gzip.open", mock_content_two):
        _as = as_repo.load_as(ASN(65537))

    assert _as.asn == ASN(65537)
    assert _as.country_of_registry == Alpha2Code("CA")


def test_when_file_has_multiple_ases_returns_existent_as(
    as_repo: FileASRepository,
    mock_content_three: Any,
) -> None:
    with patch("gzip.open", mock_content_three):
        _as = as_repo.load_as(ASN(65537))

    assert _as.asn == ASN(65537)
    assert _as.country_of_registry == Alpha2Code("CA")
