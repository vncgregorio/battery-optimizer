from enum import Enum

from battery_optimizer.domain.battery import BatterySpec


class Action(Enum):
    IDLE = "idle"
    CHARGE = "charge"
    DISCHARGE = "discharge"


def percentile(values: list[float], target_percentile: float) -> float:
    sorted_values = sorted(values)
    number_of_values = len(sorted_values)
    if number_of_values == 1:
        return sorted_values[0]

    rank = (target_percentile / 100) * (number_of_values - 1)
    lower_index = int(rank)
    upper_index = min(lower_index + 1, number_of_values - 1)
    fraction = rank - lower_index

    return sorted_values[lower_index] + (sorted_values[upper_index] - sorted_values[lower_index]) * fraction


def maximum_sustainable_power_megawatts(
    action: Action,
    battery_spec: BatterySpec,
    state_of_charge_megawatt_hours: float,
    duration_hours: float,
) -> float:
    if action is Action.CHARGE:
        storage_headroom_megawatt_hours = (
            battery_spec.maximum_storage_energy_megawatt_hours - state_of_charge_megawatt_hours
        )
        energy_limited_power_megawatts = storage_headroom_megawatt_hours / (
            duration_hours * (1 - battery_spec.charging_efficiency_loss_fraction)
        )
        return max(0.0, min(battery_spec.maximum_charge_power_megawatts, energy_limited_power_megawatts))

    if action is Action.DISCHARGE:
        energy_limited_power_megawatts = (
            state_of_charge_megawatt_hours * (1 - battery_spec.discharging_efficiency_loss_fraction)
        ) / duration_hours
        return max(0.0, min(battery_spec.maximum_discharge_power_megawatts, energy_limited_power_megawatts))

    return 0.0


def decide_action(price: float, cheap_threshold: float, expensive_threshold: float) -> Action:
    if price < cheap_threshold:
        return Action.CHARGE
    if price > expensive_threshold:
        return Action.DISCHARGE
    return Action.IDLE
