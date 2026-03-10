from cc_calc.global_centrality import GlobalCentrality


def test_centrality_starts_at_zero() -> None:
    gc = GlobalCentrality()
    assert int(gc) == 0


def test_when_centrality_is_incremented_retains_increment() -> None:
    gc = GlobalCentrality()
    gc += 1
    assert int(gc) == 1


def test_when_incremented_twice_resulting_centrality_is_sum_of_points() -> None:
    gc = GlobalCentrality()
    gc += 1
    gc += 2
    assert int(gc) == 3
