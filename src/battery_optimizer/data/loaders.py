import openpyxl

from battery_optimizer.domain.battery import BatterySpec

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
