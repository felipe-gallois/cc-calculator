import pytest
from pytest_mock import MockerFixture

from cc_calc.core import AS, ASN, Alpha2Code
from cc_calc.repo._as_repo import ASDB, ASDTO, ASRepo


@pytest.mark.parametrize(
    "dto_list,expected_as",
    [
        ([ASDTO(65536, "BR")], AS(ASN(65536), Alpha2Code("BR"))),
        (
            [ASDTO(65536, "US"), ASDTO(65537, "BR")],
            AS(ASN(65536), Alpha2Code("US")),
        ),
    ],
)
def test_it_returns_as_if_in_db_yield(
    mocker: MockerFixture, dto_list: list[ASDTO], expected_as: AS
) -> None:
    mock_db = mocker.create_autospec(ASDB)
    mock_db.load_all_ases.return_value = iter(dto_list)

    repo = ASRepo(mock_db)

    _as = repo.load_as(ASN(65536))

    assert _as == expected_as
