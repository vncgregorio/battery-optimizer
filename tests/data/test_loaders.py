from datetime import datetime

import openpyxl
import pytest

from battery_optimizer.data.loaders import load_battery_spec, load_market_one_prices


@pytest.fixture
def battery_parameters_workbook_path(tmp_path):
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.append(["", "Values", "Units", "Description"])
    worksheet.append(["Max charging rate", 2, "MW", "The maximum power that the battery can import"])
    worksheet.append(["Max discharging rate", 2, "MW", "The maximum power that the battery can export"])
    worksheet.append(["Max storage volume", 4, "MWh", "Maximum volume of energy that the battery can store"])
    worksheet.append(["Battery charging efficiency", 0.05, "-", "Fraction of energy lost while charging"])
    worksheet.append(["Battery discharging efficiency", 0.05, "-", "Fraction of energy lost while discharging"])
    worksheet.append(["Lifetime (1)", 10, "years", "Maximum battery lifetime in years"])

    workbook_path = tmp_path / "battery_parameters.xlsx"
    workbook.save(workbook_path)
    return workbook_path


def test_load_battery_spec_reads_the_relevant_rows(battery_parameters_workbook_path):
    battery_spec = load_battery_spec(battery_parameters_workbook_path)

    assert battery_spec.maximum_charge_power_megawatts == 2
    assert battery_spec.maximum_discharge_power_megawatts == 2
    assert battery_spec.maximum_storage_energy_megawatt_hours == 4
    assert battery_spec.charging_efficiency_loss_fraction == 0.05
    assert battery_spec.discharging_efficiency_loss_fraction == 0.05


@pytest.fixture
def market_prices_workbook_path(tmp_path):
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "Half-hourly data"
    worksheet.append([None, "Market 1 Price [£/MWh]"])
    worksheet.append([datetime(2018, 1, 1, 0, 0), 48.47])
    worksheet.append([datetime(2018, 1, 1, 0, 30), 49.81])

    workbook_path = tmp_path / "market_prices.xlsx"
    workbook.save(workbook_path)
    return workbook_path


def test_load_market_one_prices_reads_every_half_hourly_row(market_prices_workbook_path):
    price_points = load_market_one_prices(market_prices_workbook_path)

    assert len(price_points) == 2
    assert price_points[0].period_start == datetime(2018, 1, 1, 0, 0)
    assert price_points[0].period_duration_hours == 0.5
    assert price_points[0].price_pounds_per_megawatt_hour == 48.47
    assert price_points[1].period_start == datetime(2018, 1, 1, 0, 30)
