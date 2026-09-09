from datetime import datetime, timedelta

import pytest

from battery_optimizer.dispatch import Action, decide_action, maximum_sustainable_power_megawatts, percentile, simulate
from battery_optimizer.domain.battery import BatterySpec
from battery_optimizer.domain.market import PricePoint


def test_percentile_of_a_single_value_is_that_value():
    assert percentile([10.0], 20) == 10.0


def test_percentile_interpolates_between_the_two_nearest_ranks():
    assert percentile([10.0, 20.0, 30.0, 40.0], 25) == pytest.approx(17.5)


@pytest.fixture
def battery_spec():
    return BatterySpec(
        maximum_charge_power_megawatts=2.0,
        maximum_discharge_power_megawatts=2.0,
        maximum_storage_energy_megawatt_hours=4.0,
        charging_efficiency_loss_fraction=0.05,
        discharging_efficiency_loss_fraction=0.05,
    )


def test_charging_power_is_capped_by_the_maximum_rate_when_storage_headroom_is_ample(battery_spec):
    power = maximum_sustainable_power_megawatts(
        action=Action.CHARGE, battery_spec=battery_spec, state_of_charge_megawatt_hours=0.0, duration_hours=0.5
    )

    assert power == pytest.approx(2.0)


def test_discharging_power_is_capped_by_the_available_stored_energy(battery_spec):
    power = maximum_sustainable_power_megawatts(
        action=Action.DISCHARGE, battery_spec=battery_spec, state_of_charge_megawatt_hours=0.1, duration_hours=1.0
    )

    assert power == pytest.approx(0.1 * 0.95)


def test_decide_action_charges_when_price_is_below_the_cheap_threshold():
    assert decide_action(price=10.0, cheap_threshold=20.0, expensive_threshold=80.0) is Action.CHARGE


def test_decide_action_discharges_when_price_is_above_the_expensive_threshold():
    assert decide_action(price=90.0, cheap_threshold=20.0, expensive_threshold=80.0) is Action.DISCHARGE


def test_decide_action_stays_idle_between_the_thresholds():
    assert decide_action(price=50.0, cheap_threshold=20.0, expensive_threshold=80.0) is Action.IDLE


def test_simulate_charges_on_a_cheap_price_and_discharges_on_an_expensive_one(battery_spec):
    start = datetime(2018, 1, 1)
    prices = [10.0, 10.0, 10.0, 1.0, 200.0]
    price_points = [
        PricePoint(period_start=start + timedelta(minutes=30 * step), period_duration_hours=0.5, price_pounds_per_megawatt_hour=price)
        for step, price in enumerate(prices)
    ]

    records = simulate(battery_spec, price_points)

    assert [record.action for record in records[:3]] == [Action.IDLE] * 3

    assert records[3].action is Action.CHARGE
    assert records[3].power_megawatts == pytest.approx(2.0)
    assert records[3].state_of_charge_megawatt_hours == pytest.approx(0.95)

    assert records[4].action is Action.DISCHARGE
    assert records[4].state_of_charge_megawatt_hours == pytest.approx(0.0)
