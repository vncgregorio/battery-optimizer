import pytest

from battery_optimizer.dispatch import Action, maximum_sustainable_power_megawatts, percentile
from battery_optimizer.domain.battery import BatterySpec


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
