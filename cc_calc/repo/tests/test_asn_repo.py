import pytest
from pytest_mock import MockerFixture

from cc_calc.core import ASN
from cc_calc.repo._asn_repo import ASNDB, ASNRepo
from cc_calc.repo._ip_block_repo import ASNDTO


@pytest.mark.parametrize(
    "dto_list,expected_asns",
    [
        ([65536], [ASN(65536)]),
        ([65536, 65537], [ASN(65536), ASN(65537)]),
    ],
)
def test_when_db_yields_rels_it_builds_asn_set(
    mocker: MockerFixture, dto_list: list[ASNDTO], expected_asns: list[ASN]
) -> None:
    db_mock = mocker.create_autospec(ASNDB)
    db_mock.load_all_asns.return_value = iter(dto_list)

    repo = ASNRepo(db_mock)

    asns = repo.load_all_asns()

    assert asns == set(expected_asns)
