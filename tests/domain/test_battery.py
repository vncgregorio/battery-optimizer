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


def test_battery_spec_exposes_the_given_limits(battery_spec):
    assert battery_spec.maximum_charge_power_megawatts == 2.0
    assert battery_spec.maximum_discharge_power_megawatts == 2.0
    assert battery_spec.maximum_storage_energy_megawatt_hours == 4.0
    assert battery_spec.charging_efficiency_loss_fraction == 0.05
    assert battery_spec.discharging_efficiency_loss_fraction == 0.05


def test_battery_spec_rejects_a_non_positive_limit():
    with pytest.raises(ValueError):
        BatterySpec(
            maximum_charge_power_megawatts=0.0,
            maximum_discharge_power_megawatts=2.0,
            maximum_storage_energy_megawatt_hours=4.0,
            charging_efficiency_loss_fraction=0.05,
            discharging_efficiency_loss_fraction=0.05,
        )


def test_battery_spec_rejects_an_efficiency_loss_outside_the_unit_range():
    with pytest.raises(ValueError):
        BatterySpec(
            maximum_charge_power_megawatts=2.0,
            maximum_discharge_power_megawatts=2.0,
            maximum_storage_energy_megawatt_hours=4.0,
            charging_efficiency_loss_fraction=1.0,
            discharging_efficiency_loss_fraction=0.05,
        )


def test_battery_state_defaults_to_empty(battery_spec):
    battery_state = BatteryState(battery_spec=battery_spec)

    assert battery_state.state_of_charge_megawatt_hours == 0.0


def test_battery_state_rejects_a_state_of_charge_outside_the_valid_range(battery_spec):
    with pytest.raises(ValueError):
        BatteryState(battery_spec=battery_spec, state_of_charge_megawatt_hours=4.1)
    with pytest.raises(ValueError):
        BatteryState(battery_spec=battery_spec, state_of_charge_megawatt_hours=-0.1)


def test_charging_stores_energy_reduced_by_the_charging_efficiency_loss(battery_spec):
    battery_state = BatteryState(battery_spec=battery_spec)

    battery_state.charge(power_megawatts=2.0, duration_hours=0.5)

    assert battery_state.state_of_charge_megawatt_hours == pytest.approx(2.0 * 0.5 * 0.95)


def test_discharging_removes_more_stored_energy_than_it_delivers_to_the_grid(battery_spec):
    battery_state = BatteryState(battery_spec=battery_spec, state_of_charge_megawatt_hours=4.0)

    battery_state.discharge(power_megawatts=2.0, duration_hours=0.5)

    delivered_to_grid_megawatt_hours = 2.0 * 0.5
    drawn_from_storage_megawatt_hours = delivered_to_grid_megawatt_hours / 0.95
    assert battery_state.state_of_charge_megawatt_hours == pytest.approx(4.0 - drawn_from_storage_megawatt_hours)


def test_charging_and_discharging_beyond_available_capacity_or_energy_raise(battery_spec):
    almost_full_battery = BatteryState(battery_spec=battery_spec, state_of_charge_megawatt_hours=3.9)
    with pytest.raises(ValueError):
        almost_full_battery.charge(power_megawatts=2.0, duration_hours=1.0)

    almost_empty_battery = BatteryState(battery_spec=battery_spec, state_of_charge_megawatt_hours=0.1)
    with pytest.raises(ValueError):
        almost_empty_battery.discharge(power_megawatts=2.0, duration_hours=1.0)


def test_charging_and_discharging_above_the_maximum_rate_raise_even_with_spare_capacity(battery_spec):
    empty_battery = BatteryState(battery_spec=battery_spec)
    with pytest.raises(ValueError):
        empty_battery.charge(power_megawatts=2.1, duration_hours=0.5)

    full_battery = BatteryState(battery_spec=battery_spec, state_of_charge_megawatt_hours=4.0)
    with pytest.raises(ValueError):
        full_battery.discharge(power_megawatts=2.1, duration_hours=0.5)
