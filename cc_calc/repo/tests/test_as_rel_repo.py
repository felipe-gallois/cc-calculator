import pytest
from pytest_mock import MockerFixture

from cc_calc.core import ASN, ASRel, RelType
from cc_calc.repo._as_rel_repo import ASRelGraphRepo
from cc_calc.repo._database import ASRelDB
from cc_calc.repo._dto import ASRelDTO, RelTypeDTO


@pytest.mark.parametrize(
    "rels,edges",
    [
        (
            [ASRelDTO(65536, 65537, RelTypeDTO.P2P)],
            {ASRel(ASN(65536), ASN(65537), RelType.P2P)},
        ),
        (
            [ASRelDTO(65537, 65538, RelTypeDTO.P2C)],
            {ASRel(ASN(65537), ASN(65538), RelType.P2C)},
        ),
        (
            [
                ASRelDTO(65536, 65537, RelTypeDTO.P2C),
                ASRelDTO(65537, 65538, RelTypeDTO.P2C),
            ],
            {
                ASRel(ASN(65536), ASN(65537), RelType.P2C),
                ASRel(ASN(65537), ASN(65538), RelType.P2C),
            },
        ),
    ],
)
def test_when_db_yields_rels_it_builds_rel_graph(
    mocker: MockerFixture, rels: list[ASRelDTO], edges: set[ASRel]
) -> None:
    db_mock = mocker.create_autospec(ASRelDB)
    db_mock.load_rels.return_value = iter(rels)

    repo = ASRelGraphRepo(db_mock)

    rel_graph = repo.load_rel_graph()

    assert rel_graph.edges == edges
