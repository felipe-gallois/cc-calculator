import gzip
import zlib

import pytest
from pytest_mock import MockerFixture

from cc_calc.db._caida_as_org_db import CaidaASOrgDB
from cc_calc.repo import ASDTO, InvalidDBDataFormat, UnreachableDB

TEST_INPUT = [
    (
        "#\n"
        "# format:org_id|changed|org_name|country|source\n"
        "@aut-65536-ARIN|19700101|Company Inc.|US|ARIN\n"
        "# format:aut|changed|aut_name|org_id|opaque_id|source\n"
        "65536|19700101|COM|@aut-65536-ARIN|1234567_ARIN|ARIN\n"
    ),
    (
        "#\n"
        "# format:org_id|changed|org_name|country|source\n"
        "@aut-65537-ARIN|19700101|Company Inc.|CA|ARIN\n"
        "# format:aut|changed|aut_name|org_id|opaque_id|source\n"
        "65537|19700101|COM|@aut-65537-ARIN|1234567_ARIN|ARIN\n"
    ),
    (
        "#\n"
        "# format:org_id|changed|org_name|country|source\n"
        "@aut-65536-ARIN|19700101|Company Inc.|US|ARIN\n"
        "@aut-65537-ARIN|19700101|Company Inc.|CA|ARIN\n"
        "# format:aut|changed|aut_name|org_id|opaque_id|source\n"
        "65536|19700101|COM|@aut-65536-ARIN|1234567_ARIN|ARIN\n"
        "65537|19700101|COM|@aut-65537-ARIN|1234567_ARIN|ARIN\n"
    ),
    (
        "#\n"
        "# format:org_id|changed|org_name|country|source\n"
        "@aut-65536-ARIN|19700101|Company Inc.|US|ARIN\n"
        "# format:aut|changed|aut_name|org_id|opaque_id|source\n"
    ),
    (
        "#\n"
        "# format:org_id|changed|org_name|country|source\n"
        "@aut-65536-ARIN|19700101|Company Inc.|US|ARIN\n"
        "@aut-65537-ARIN|19700101|Company Inc.|CA|ARIN\n"
        "# format:aut|changed|aut_name|org_id|opaque_id|source\n"
        "65536|19700101|COM|@aut-65536-ARIN|1234567_ARIN|ARIN\n"
    ),
    (
        "#\n"
        "# format:org_id|changed|org_name|country|source\n"
        "# format:aut|changed|aut_name|org_id|opaque_id|source\n"
        "65536|19700101|COM|@aut-65536-ARIN|1234567_ARIN|ARIN\n"
    ),
    (
        "#\n"
        "# format:org_id|changed|org_name|country|source\n"
        "@aut-65536-ARIN|19700101|Company Inc.|US|ARIN\n"
        "# format:aut|changed|aut_name|org_id|opaque_id|source\n"
        "65536|19700101|COM|@aut-65536-ARIN|1234567_ARIN|ARIN\n"
        "65537|19700101|COM|@aut-65537-ARIN|1234567_ARIN|ARIN\n"
    ),
]

TEST_EXPECTED_OUTPUT = [
    [ASDTO(65536, "US")],
    [ASDTO(65537, "CA")],
    [ASDTO(65536, "US"), ASDTO(65537, "CA")],
    [],
    [ASDTO(65536, "US")],
    [],
    [ASDTO(65536, "US")],
]


@pytest.mark.parametrize("input,expected_output", zip(TEST_INPUT, TEST_EXPECTED_OUTPUT))
def test_when_as_registered_in_us_is_in_file_returns_as(
    mocker: MockerFixture, input: str, expected_output: list[ASDTO]
) -> None:
    mock_open = mocker.mock_open(read_data=input)
    mocker.patch(
        "cc_calc.db._caida_as_org_db.gzip.open",
        return_value=mock_open.return_value,
    )

    db = CaidaASOrgDB("")

    it = db.load_all_ases()

    assert list(it) == expected_output


@pytest.mark.parametrize("exception", [FileNotFoundError, PermissionError])
def test_when_gzip_cannot_reach_data_raises_exception(
    mocker: MockerFixture, exception: Exception
) -> None:
    mocker.patch(
        "cc_calc.db._caida_as_org_db.gzip.open",
        side_effect=exception,
    )

    db = CaidaASOrgDB("")

    with pytest.raises(UnreachableDB):
        next(db.load_all_ases())


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
        "cc_calc.db._caida_as_org_db.gzip.open",
        side_effect=exception,
    )

    db = CaidaASOrgDB("")

    with pytest.raises(InvalidDBDataFormat):
        next(db.load_all_ases())


def test_when_file_is_incorrectly_formatted_raises_exception(
    mocker: MockerFixture,
) -> None:
    invalid_input = (
        "#\n"
        "# format:org_id|changed|org_name|country|source\n"
        "@aut-65536-ARIN|19700101|Company Inc.|US|ARIN\n"
        "# format:aut|changed|aut_name|org_id|opaque_id|source\n"
        "65536\n"
    )

    mock_open = mocker.mock_open(read_data=invalid_input)
    mocker.patch(
        "cc_calc.db._caida_as_org_db.gzip.open",
        return_value=mock_open.return_value,
    )

    db = CaidaASOrgDB("")

    with pytest.raises(InvalidDBDataFormat):
        next(db.load_all_ases())
