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


def test_battery_state_defaults_to_empty(battery_spec):
    battery_state = BatteryState(battery_spec=battery_spec)

    assert battery_state.state_of_charge_megawatt_hours == 0.0


def test_battery_state_accepts_a_state_of_charge_within_capacity(battery_spec):
    battery_state = BatteryState(battery_spec=battery_spec, state_of_charge_megawatt_hours=4.0)

    assert battery_state.state_of_charge_megawatt_hours == 4.0


def test_battery_state_rejects_a_state_of_charge_above_capacity(battery_spec):
    with pytest.raises(ValueError):
        BatteryState(battery_spec=battery_spec, state_of_charge_megawatt_hours=4.1)


def test_battery_state_rejects_a_negative_state_of_charge(battery_spec):
    with pytest.raises(ValueError):
        BatteryState(battery_spec=battery_spec, state_of_charge_megawatt_hours=-0.1)
