import pytest

from battery_optimizer.dispatch import percentile


def test_percentile_of_a_single_value_is_that_value():
    assert percentile([10.0], 20) == 10.0


def test_percentile_interpolates_between_the_two_nearest_ranks():
    assert percentile([10.0, 20.0, 30.0, 40.0], 25) == pytest.approx(17.5)
