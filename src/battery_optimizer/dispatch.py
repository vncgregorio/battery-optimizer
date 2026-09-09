from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from battery_optimizer.domain.battery import BatterySpec, BatteryState
from battery_optimizer.domain.market import PricePoint


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


@dataclass(frozen=True)
class DispatchRecord:
    period_start: datetime
    action: Action
    power_megawatts: float
    price_pounds_per_megawatt_hour: float
    duration_hours: float
    state_of_charge_megawatt_hours: float


def simulate(
    battery_spec: BatterySpec,
    price_points: list[PricePoint],
    cheap_percentile: float = 20,
    expensive_percentile: float = 80,
) -> list[DispatchRecord]:
    all_prices = [price_point.price_pounds_per_megawatt_hour for price_point in price_points]
    cheap_threshold = percentile(all_prices, cheap_percentile)
    expensive_threshold = percentile(all_prices, expensive_percentile)

    battery_state = BatteryState(battery_spec=battery_spec)
    records = []
    for price_point in price_points:
        action = decide_action(price_point.price_pounds_per_megawatt_hour, cheap_threshold, expensive_threshold)
        power_megawatts = maximum_sustainable_power_megawatts(
            action, battery_spec, battery_state.state_of_charge_megawatt_hours, price_point.period_duration_hours
        )

        if action is Action.CHARGE:
            battery_state.charge(power_megawatts, price_point.period_duration_hours)
        elif action is Action.DISCHARGE:
            battery_state.discharge(power_megawatts, price_point.period_duration_hours)

        records.append(
            DispatchRecord(
                period_start=price_point.period_start,
                action=action,
                power_megawatts=power_megawatts,
                price_pounds_per_megawatt_hour=price_point.price_pounds_per_megawatt_hour,
                duration_hours=price_point.period_duration_hours,
                state_of_charge_megawatt_hours=battery_state.state_of_charge_megawatt_hours,
            )
        )
    return records
