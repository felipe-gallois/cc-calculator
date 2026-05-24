import pytest
from pytest_mock import MockerFixture

from cc_calc.db._caida_as_rel_db import CaidaASRelDB
from cc_calc.repo import ASRelDTO, ASRelLoadingError, RelTypeDTO


def get_string(input: ASRelDTO) -> str:
    rel_type_int = 0 if input.rel_type is RelTypeDTO.P2P else -1
    return f"{input.src_as}|{input.dst_as}|{rel_type_int}|bgp"


def get_multiline_string(input: list[ASRelDTO]) -> str:
    input_strs = [get_string(dto) for dto in input]
    return "\n".join(input_strs)


class TestLoadingRels:
    def test_when_bz2_raises_exception_it_wraps_the_exception(
        self,
        mocker: MockerFixture,
    ) -> None:
        mocker.patch(
            "cc_calc.db._caida_as_rel_db.bz2.open",
            side_effect=FileNotFoundError(""),
        )

        db = CaidaASRelDB("")

        with pytest.raises(ASRelLoadingError):
            next(db.load_rels())

    @pytest.mark.parametrize("input", ["", "# 65536|65537|0|bgp"])
    def test_when_file_has_no_as_rels_yields_nothing(
        self, mocker: MockerFixture, input: ASRelDTO
    ) -> None:
        mock_open = mocker.mock_open(read_data=input)

        mocker.patch(
            "cc_calc.db._caida_as_rel_db.bz2.open",
            return_value=mock_open.return_value,
        )

        db = CaidaASRelDB("")

        it = db.load_rels()

        with pytest.raises(StopIteration):
            next(it)

    @pytest.mark.parametrize(
        "input",
        [
            ASRelDTO(65536, 65537, RelTypeDTO.P2P),
            ASRelDTO(65537, 65538, RelTypeDTO.P2C),
        ],
    )
    def test_when_file_has_one_as_rel_yields_single_dto(
        self, mocker: MockerFixture, input: ASRelDTO
    ) -> None:
        mock_open = mocker.mock_open(read_data=get_string(input))

        mocker.patch(
            "cc_calc.db._caida_as_rel_db.bz2.open",
            return_value=mock_open.return_value,
        )

        db = CaidaASRelDB("")

        it = db.load_rels()

        assert list(it) == [input]

    def test_when_file_has_multiple_as_rels_yields_multiple_dtos(
        self,
        mocker: MockerFixture,
    ) -> None:
        input = [
            ASRelDTO(65536, 65537, RelTypeDTO.P2P),
            ASRelDTO(65537, 65538, RelTypeDTO.P2P),
        ]

        mock_open = mocker.mock_open(read_data=get_multiline_string(input))

        mocker.patch(
            "cc_calc.db._caida_as_rel_db.bz2.open",
            return_value=mock_open.return_value,
        )

        db = CaidaASRelDB("")

        it = db.load_rels()

        assert list(it) == input


class TestLoadingAllASNs:
    def test_when_bz2_raises_exception_it_wraps_the_exception(
        self,
        mocker: MockerFixture,
    ) -> None:
        mocker.patch(
            "cc_calc.db._caida_as_rel_db.bz2.open",
            side_effect=FileNotFoundError(""),
        )

        db = CaidaASRelDB("")

        with pytest.raises(ASRelLoadingError):
            next(db.load_all_asns())

    @pytest.mark.parametrize("input", ["", "# 65536|65537|0|bgp"])
    def test_when_file_has_no_as_rels_yields_nothing(
        self, mocker: MockerFixture, input: ASRelDTO
    ) -> None:
        mock_open = mocker.mock_open(read_data=input)

        mocker.patch(
            "cc_calc.db._caida_as_rel_db.bz2.open",
            return_value=mock_open.return_value,
        )

        db = CaidaASRelDB("")

        it = db.load_all_asns()

        with pytest.raises(StopIteration):
            next(it)

    @pytest.mark.parametrize(
        "input",
        [
            ASRelDTO(65536, 65537, RelTypeDTO.P2P),
            ASRelDTO(65537, 65538, RelTypeDTO.P2C),
        ],
    )
    def test_when_file_has_one_as_rel_yields_two_dtos(
        self, mocker: MockerFixture, input: ASRelDTO
    ) -> None:
        mock_open = mocker.mock_open(read_data=get_string(input))

        mocker.patch(
            "cc_calc.db._caida_as_rel_db.bz2.open",
            return_value=mock_open.return_value,
        )

        db = CaidaASRelDB("")

        it = db.load_all_asns()

        assert list(it) == [input.src_as, input.dst_as]

    def test_when_file_has_multiple_as_rels_yields_multiple_dtos(
        self,
        mocker: MockerFixture,
    ) -> None:
        input = [
            ASRelDTO(65536, 65537, RelTypeDTO.P2P),
            ASRelDTO(65537, 65538, RelTypeDTO.P2P),
        ]

        mock_open = mocker.mock_open(read_data=get_multiline_string(input))

        mocker.patch(
            "cc_calc.db._caida_as_rel_db.bz2.open",
            return_value=mock_open.return_value,
        )

        db = CaidaASRelDB("")

        it = db.load_all_asns()

        assert list(it) == [65536, 65537, 65537, 65538]
