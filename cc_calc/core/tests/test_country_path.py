from cc_calc.core._country_code import Alpha2Code
from cc_calc.core._country_path import CountryPath


class TestCreateCountryPath:
    def test_when_sequence_only_has_none_returns_empty_path(self) -> None:
        path = CountryPath([None])
        assert path == CountryPath([])


class TestIterateCountryPath:
    def test_when_country_sequence_does_not_repeat_iterates_equally_to_path(
        self,
    ) -> None:
        seq = [Alpha2Code("CA"), Alpha2Code("US"), Alpha2Code("BR")]
        path = CountryPath(seq)

        for country_a, country_b in zip(seq, path):
            assert country_a == country_b

    def test_when_sequence_repeats_iterates_shortened_sequence(self) -> None:
        path = CountryPath(
            [
                Alpha2Code("CA"),
                Alpha2Code("CA"),
                Alpha2Code("US"),
                Alpha2Code("BR"),
                Alpha2Code("BR"),
            ]
        )

        seq = [
            Alpha2Code("CA"),
            Alpha2Code("US"),
            Alpha2Code("BR"),
        ]

        for country_a, country_b in zip(path, seq):
            assert country_a == country_b

    def test_when_sequence_goes_through_a_country_twice_path_does_also(self) -> None:
        path = CountryPath(
            [
                Alpha2Code("CA"),
                Alpha2Code("US"),
                Alpha2Code("CA"),
            ]
        )

        seq = [
            Alpha2Code("CA"),
            Alpha2Code("US"),
            Alpha2Code("CA"),
        ]

        for country_a, country_b in zip(path, seq):
            assert country_a == country_b


class TestCompareCountryPath:
    def test_equality_with_another_type_returns_false(self) -> None:
        seq = [Alpha2Code("CA"), Alpha2Code("US"), Alpha2Code("BR")]
        path = CountryPath(seq)

        assert path != seq

    def test_when_country_sequence_is_different_return_not_equal(self) -> None:
        seq_a = CountryPath([Alpha2Code("CA"), Alpha2Code("US"), Alpha2Code("BR")])
        seq_b = CountryPath([Alpha2Code("CA"), Alpha2Code("US"), Alpha2Code("MX")])

        assert seq_a != seq_b

    def test_when_country_sequence_has_repetition_shortens_sequence(self) -> None:
        path = CountryPath(
            [
                Alpha2Code("CA"),
                Alpha2Code("CA"),
                Alpha2Code("US"),
                Alpha2Code("BR"),
                Alpha2Code("BR"),
            ]
        )

        assert path == CountryPath(
            [Alpha2Code("CA"), Alpha2Code("US"), Alpha2Code("BR")]
        )


class TestListCountryPathCountries:
    def test_when_path_has_interleaved_countries_returns_countries(self) -> None:
        path = CountryPath(
            [
                Alpha2Code("CA"),
                Alpha2Code("US"),
                Alpha2Code("CA"),
            ]
        )

        assert path.countries == {Alpha2Code("CA"), Alpha2Code("US")}

    def test_when_path_has_none_does_not_return_none_in_countries(self) -> None:
        path = CountryPath(
            [
                Alpha2Code("CA"),
                Alpha2Code("US"),
                None,
            ]
        )

        assert path.countries == {Alpha2Code("CA"), Alpha2Code("US")}
