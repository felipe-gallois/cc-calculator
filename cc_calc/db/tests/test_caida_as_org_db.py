import pytest
from pytest_mock import MockerFixture

from cc_calc.core import ASLoadingError
from cc_calc.db._caida_as_org_db import CaidaASOrgDB
from cc_calc.repo import ASDTO


def test_when_gzip_raises_exception_it_wraps_the_exception(
    mocker: MockerFixture,
) -> None:
    mocker.patch(
        "cc_calc.db._caida_as_org_db.gzip.open",
        side_effect=FileNotFoundError,
    )

    db = CaidaASOrgDB("")

    with pytest.raises(ASLoadingError):
        next(db.load_all_ases())


@pytest.mark.parametrize(
    "input,expected_output",
    [
        (
            (
                "#\n"
                "# format:org_id|changed|org_name|country|source\n"
                "@aut-65536-ARIN|19700101|Company Inc.|US|ARIN\n"
                "# format:aut|changed|aut_name|org_id|opaque_id|source\n"
                "65536|19700101|COM|@aut-65536-ARIN|1234567_ARIN|ARIN\n"
            ),
            ASDTO(65536, "US"),
        ),
        (
            (
                "#\n"
                "# format:org_id|changed|org_name|country|source\n"
                "@aut-65537-ARIN|19700101|Company Inc.|CA|ARIN\n"
                "# format:aut|changed|aut_name|org_id|opaque_id|source\n"
                "65537|19700101|COM|@aut-65537-ARIN|1234567_ARIN|ARIN\n"
            ),
            ASDTO(65537, "CA"),
        ),
    ],
)
def test_when_as_registered_in_us_is_in_file_returns_as(
    mocker: MockerFixture, input: str, expected_output: ASDTO
) -> None:
    mock_open = mocker.mock_open(read_data=input)
    mocker.patch(
        "cc_calc.db._caida_as_org_db.gzip.open",
        return_value=mock_open.return_value,
    )

    db = CaidaASOrgDB("")

    it = db.load_all_ases()

    assert list(it) == [expected_output]


def test_when_file_has_multiple_ases_returns_existent_as(mocker: MockerFixture) -> None:
    input = (
        "#\n"
        "# format:org_id|changed|org_name|country|source\n"
        "@aut-65536-ARIN|19700101|Company Inc.|US|ARIN\n"
        "@aut-65537-ARIN|19700101|Company Inc.|CA|ARIN\n"
        "# format:aut|changed|aut_name|org_id|opaque_id|source\n"
        "65536|19700101|COM|@aut-65536-ARIN|1234567_ARIN|ARIN\n"
        "65537|19700101|COM|@aut-65537-ARIN|1234567_ARIN|ARIN\n"
    )

    mock_open = mocker.mock_open(read_data=input)
    mocker.patch(
        "cc_calc.db._caida_as_org_db.gzip.open",
        return_value=mock_open.return_value,
    )

    db = CaidaASOrgDB("")

    it = db.load_all_ases()

    assert list(it) == [ASDTO(65536, "US"), ASDTO(65537, "CA")]
