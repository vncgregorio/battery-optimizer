from dataclasses import dataclass

_POSITIVE_FIELD_NAMES = (
    "maximum_charge_power_megawatts",
    "maximum_discharge_power_megawatts",
    "maximum_storage_energy_megawatt_hours",
)
_UNIT_RANGE_FIELD_NAMES = (
    "charging_efficiency_loss_fraction",
    "discharging_efficiency_loss_fraction",
)


@dataclass(frozen=True)
class BatterySpec:
    maximum_charge_power_megawatts: float
    maximum_discharge_power_megawatts: float
    maximum_storage_energy_megawatt_hours: float
    charging_efficiency_loss_fraction: float
    discharging_efficiency_loss_fraction: float

    def __post_init__(self):
        for field_name in _POSITIVE_FIELD_NAMES:
            if getattr(self, field_name) <= 0:
                raise ValueError(f"{field_name} must be positive")
        for field_name in _UNIT_RANGE_FIELD_NAMES:
            value = getattr(self, field_name)
            if not 0 <= value < 1:
                raise ValueError(f"{field_name} must be within [0, 1)")
