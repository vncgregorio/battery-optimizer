import openpyxl

from battery_optimizer.domain.battery import BatterySpec
from battery_optimizer.domain.market import PricePoint

_BATTERY_PARAMETER_ROW_LABELS = {
    "Max charging rate": "maximum_charge_power_megawatts",
    "Max discharging rate": "maximum_discharge_power_megawatts",
    "Max storage volume": "maximum_storage_energy_megawatt_hours",
    "Battery charging efficiency": "charging_efficiency_loss_fraction",
    "Battery discharging efficiency": "discharging_efficiency_loss_fraction",
}


def load_battery_spec(battery_parameters_workbook_path) -> BatterySpec:
    workbook = openpyxl.load_workbook(battery_parameters_workbook_path)
    worksheet = workbook.active

    battery_spec_arguments = {}
    for row in worksheet.iter_rows(values_only=True):
        row_label = row[0]
        field_name = _BATTERY_PARAMETER_ROW_LABELS.get(row_label)
        if field_name is not None:
            battery_spec_arguments[field_name] = row[1]

    return BatterySpec(**battery_spec_arguments)


def load_market_one_prices(market_prices_workbook_path) -> list[PricePoint]:
    workbook = openpyxl.load_workbook(market_prices_workbook_path, data_only=True)
    worksheet = workbook["Half-hourly data"]

    price_points = []
    for period_start, price_pounds_per_megawatt_hour in worksheet.iter_rows(min_row=2, values_only=True):
        if period_start is None:
            continue
        price_points.append(
            PricePoint(
                period_start=period_start,
                period_duration_hours=0.5,
                price_pounds_per_megawatt_hour=price_pounds_per_megawatt_hour,
            )
        )
    return price_points
