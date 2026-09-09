import csv
from dataclasses import dataclass

from battery_optimizer.dispatch import Action, DispatchRecord


@dataclass(frozen=True)
class DispatchSummary:
    total_profit_pounds: float
    total_energy_charged_megawatt_hours: float
    total_energy_discharged_megawatt_hours: float


def summarize(records: list[DispatchRecord]) -> DispatchSummary:
    total_profit_pounds = 0.0
    total_energy_charged_megawatt_hours = 0.0
    total_energy_discharged_megawatt_hours = 0.0

    for record in records:
        energy_megawatt_hours = record.power_megawatts * record.duration_hours
        if record.action is Action.CHARGE:
            total_profit_pounds -= energy_megawatt_hours * record.price_pounds_per_megawatt_hour
            total_energy_charged_megawatt_hours += energy_megawatt_hours
        elif record.action is Action.DISCHARGE:
            total_profit_pounds += energy_megawatt_hours * record.price_pounds_per_megawatt_hour
            total_energy_discharged_megawatt_hours += energy_megawatt_hours

    return DispatchSummary(
        total_profit_pounds=total_profit_pounds,
        total_energy_charged_megawatt_hours=total_energy_charged_megawatt_hours,
        total_energy_discharged_megawatt_hours=total_energy_discharged_megawatt_hours,
    )


def write_records_csv(records: list[DispatchRecord], csv_path) -> None:
    with open(csv_path, "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            ["period_start", "action", "power_megawatts", "price_pounds_per_megawatt_hour", "state_of_charge_megawatt_hours"]
        )
        for record in records:
            writer.writerow(
                [
                    record.period_start.isoformat(),
                    record.action.value,
                    record.power_megawatts,
                    record.price_pounds_per_megawatt_hour,
                    record.state_of_charge_megawatt_hours,
                ]
            )
