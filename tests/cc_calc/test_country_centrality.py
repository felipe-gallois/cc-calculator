from cc_calc.country_centrality import CountryCentrality


def test_when_not_updated_yet_country_centrality_is_zero() -> None:
    cc = CountryCentrality()
    assert cc["US"] == 0


def test_when_updated_once_country_centrality_is_informed_value() -> None:
    cc = CountryCentrality()
    points = 1

    cc.add("US", points)

    assert cc["US"] == points


def test_when_two_countries_are_updated_once_both_return_their_centralities() -> None:
    cc = CountryCentrality()
    points_a = 1
    points_b = 2

    cc.add("CA", points_a)
    cc.add("US", points_b)

    assert cc["CA"] == points_a
    assert cc["US"] == points_b
