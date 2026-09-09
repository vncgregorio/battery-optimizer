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


def test_charging_above_the_maximum_charge_rate_raises_even_with_spare_capacity(battery_spec):
    battery_state = BatteryState(battery_spec=battery_spec)

    with pytest.raises(ValueError):
        battery_state.charge(power_megawatts=2.1, duration_hours=0.5)


def test_discharging_above_the_maximum_discharge_rate_raises_even_with_spare_energy(battery_spec):
    battery_state = BatteryState(battery_spec=battery_spec, state_of_charge_megawatt_hours=4.0)

    with pytest.raises(ValueError):
        battery_state.discharge(power_megawatts=2.1, duration_hours=0.5)
