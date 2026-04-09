from cc_calc.country_code import Alpha2Code
from cc_calc.country_path_estimation._country_path import (
    CountryPath,
    UnknownCountryEvent,
)


class TestCreateCountryPath:
    def test_when_sequence_has_none_ignores_unknown_countries(self) -> None:
        path = CountryPath([Alpha2Code("CA"), None, Alpha2Code("BR")])
        expected_path = CountryPath([Alpha2Code("CA"), Alpha2Code("BR")])
        assert path == expected_path

    def test_when_sequence_has_none_adds_unknown_country_event(self) -> None:
        path = CountryPath([Alpha2Code("CA"), None, Alpha2Code("BR")])
        assert UnknownCountryEvent() in path.events

    def test_when_sequence_does_not_have_none_does_not_add_event(self) -> None:
        path = CountryPath([Alpha2Code("CA")])
        assert UnknownCountryEvent() not in path.events

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
