import pytest

from battery_optimizer.domain.battery import BatterySpec


def test_battery_spec_exposes_the_given_limits():
    battery_spec = BatterySpec(
        maximum_charge_power_megawatts=2.0,
        maximum_discharge_power_megawatts=2.0,
        maximum_storage_energy_megawatt_hours=4.0,
        charging_efficiency_loss_fraction=0.05,
        discharging_efficiency_loss_fraction=0.05,
    )

    assert battery_spec.maximum_charge_power_megawatts == 2.0
    assert battery_spec.maximum_discharge_power_megawatts == 2.0
    assert battery_spec.maximum_storage_energy_megawatt_hours == 4.0
    assert battery_spec.charging_efficiency_loss_fraction == 0.05
    assert battery_spec.discharging_efficiency_loss_fraction == 0.05


@pytest.mark.parametrize(
    "field_name",
    [
        "maximum_charge_power_megawatts",
        "maximum_discharge_power_megawatts",
        "maximum_storage_energy_megawatt_hours",
    ],
)
def test_battery_spec_rejects_non_positive_limits(field_name):
    valid_arguments = dict(
        maximum_charge_power_megawatts=2.0,
        maximum_discharge_power_megawatts=2.0,
        maximum_storage_energy_megawatt_hours=4.0,
        charging_efficiency_loss_fraction=0.05,
        discharging_efficiency_loss_fraction=0.05,
    )
    valid_arguments[field_name] = 0.0

    with pytest.raises(ValueError):
        BatterySpec(**valid_arguments)


@pytest.mark.parametrize(
    "field_name",
    ["charging_efficiency_loss_fraction", "discharging_efficiency_loss_fraction"],
)
def test_battery_spec_rejects_efficiency_losses_outside_unit_range(field_name):
    valid_arguments = dict(
        maximum_charge_power_megawatts=2.0,
        maximum_discharge_power_megawatts=2.0,
        maximum_storage_energy_megawatt_hours=4.0,
        charging_efficiency_loss_fraction=0.05,
        discharging_efficiency_loss_fraction=0.05,
    )
    valid_arguments[field_name] = 1.0

    with pytest.raises(ValueError):
        BatterySpec(**valid_arguments)
