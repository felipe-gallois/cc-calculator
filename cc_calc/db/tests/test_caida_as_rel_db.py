import pytest
from pytest_mock import MockerFixture

from cc_calc.db._caida_as_rel_db import CaidaASRelDB
from cc_calc.repo import (
    ASRelDTO,
    InvalidDBDataFormat,
    RelTypeDTO,
    UnreachableDB,
)


def get_string(input: ASRelDTO) -> str:
    rel_type_int = 0 if input.rel_type is RelTypeDTO.P2P else -1
    return f"{input.src_as}|{input.dst_as}|{rel_type_int}|bgp"


def get_multiline_string(input: list[ASRelDTO]) -> str:
    input_strs = [get_string(dto) for dto in input]
    return "\n".join(input_strs)


class TestLoadingRels:
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

    @pytest.mark.parametrize("exception", [FileNotFoundError(""), PermissionError])
    def test_when_bz2_cannot_find_or_read_from_file_it_raises_exception(
        self, mocker: MockerFixture, exception: Exception
    ) -> None:
        mocker.patch(
            "cc_calc.db._caida_as_rel_db.bz2.open",
            side_effect=exception,
        )

        db = CaidaASRelDB("")

        with pytest.raises(UnreachableDB):
            next(db.load_rels())

    @pytest.mark.parametrize(
        "exception", [OSError, UnicodeDecodeError("utf-8", b"", 0, 1, ""), ValueError]
    )
    def test_when_bz2_cannot_recognize_format_it_raises_exception(
        self, mocker: MockerFixture, exception: Exception
    ) -> None:
        mocker.patch(
            "cc_calc.db._caida_as_rel_db.bz2.open",
            side_effect=exception,
        )

        db = CaidaASRelDB("")

        with pytest.raises(InvalidDBDataFormat):
            next(db.load_rels())

    @pytest.mark.parametrize(
        "input", ["65536|a|0|bgp", "b|65537|1|bgp", "65536|65537|2|bgp"]
    )
    def test_when_line_is_malformed_it_ignores_it(
        self, mocker: MockerFixture, input: str
    ) -> None:
        mock_open = mocker.mock_open(read_data=input)

        mocker.patch(
            "cc_calc.db._caida_as_rel_db.bz2.open",
            return_value=mock_open.return_value,
        )

        db = CaidaASRelDB("")

        it = db.load_rels()

        assert list(it) == []


class TestLoadingAllASNs:
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

    @pytest.mark.parametrize("exception", [FileNotFoundError(""), PermissionError])
    def test_when_bz2_cannot_find_or_read_from_file_it_raises_exception(
        self, mocker: MockerFixture, exception: Exception
    ) -> None:
        mocker.patch(
            "cc_calc.db._caida_as_rel_db.bz2.open",
            side_effect=exception,
        )

        db = CaidaASRelDB("")

        with pytest.raises(UnreachableDB):
            next(db.load_all_asns())

    @pytest.mark.parametrize(
        "exception", [OSError, UnicodeDecodeError("utf-8", b"", 0, 1, ""), ValueError]
    )
    def test_when_bz2_cannot_recognize_format_it_raises_exception(
        self, mocker: MockerFixture, exception: Exception
    ) -> None:
        mocker.patch(
            "cc_calc.db._caida_as_rel_db.bz2.open",
            side_effect=exception,
        )

        db = CaidaASRelDB("")

        with pytest.raises(InvalidDBDataFormat):
            next(db.load_all_asns())

    @pytest.mark.parametrize("input", ["65536|a|0|bgp", "b|65536|1|bgp"])
    def test_when_line_is_malformed_it_ignores_it(
        self, mocker: MockerFixture, input: str
    ) -> None:
        mock_open = mocker.mock_open(read_data=input)

        mocker.patch(
            "cc_calc.db._caida_as_rel_db.bz2.open",
            return_value=mock_open.return_value,
        )

        db = CaidaASRelDB("")

        it = db.load_all_asns()

        assert list(it) == [65536]
