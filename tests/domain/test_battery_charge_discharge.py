import pytest

from battery_optimizer.domain.battery import BatterySpec, BatteryState


@pytest.fixture
def battery_spec():
    return BatterySpec(
        maximum_charge_power_megawatts=2.0,
        maximum_discharge_power_megawatts=2.0,
        maximum_storage_energy_megawatt_hours=4.0,
        charging_efficiency_loss_fraction=0.05,
        discharging_efficiency_loss_fraction=0.05,
    )


def test_charging_stores_energy_reduced_by_the_charging_efficiency_loss(battery_spec):
    battery_state = BatteryState(battery_spec=battery_spec)

    battery_state.charge(power_megawatts=2.0, duration_hours=0.5)

    assert battery_state.state_of_charge_megawatt_hours == pytest.approx(2.0 * 0.5 * 0.95)


def test_discharging_removes_more_stored_energy_than_it_delivers_to_the_grid(battery_spec):
    battery_state = BatteryState(battery_spec=battery_spec, state_of_charge_megawatt_hours=4.0)

    battery_state.discharge(power_megawatts=2.0, duration_hours=0.5)

    delivered_to_grid_megawatt_hours = 2.0 * 0.5
    drawn_from_storage_megawatt_hours = delivered_to_grid_megawatt_hours / 0.95
    assert battery_state.state_of_charge_megawatt_hours == pytest.approx(
        4.0 - drawn_from_storage_megawatt_hours
    )


def test_charging_beyond_storage_capacity_raises(battery_spec):
    battery_state = BatteryState(battery_spec=battery_spec, state_of_charge_megawatt_hours=3.9)

    with pytest.raises(ValueError):
        battery_state.charge(power_megawatts=2.0, duration_hours=1.0)


def test_discharging_beyond_available_stored_energy_raises(battery_spec):
    battery_state = BatteryState(battery_spec=battery_spec, state_of_charge_megawatt_hours=0.1)

    with pytest.raises(ValueError):
        battery_state.discharge(power_megawatts=2.0, duration_hours=1.0)
