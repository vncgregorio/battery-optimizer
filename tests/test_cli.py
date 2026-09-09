import csv
from datetime import datetime

import openpyxl
import pytest

from battery_optimizer.cli import main


@pytest.fixture
def battery_parameters_path(tmp_path):
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.append(["", "Values", "Units", "Description"])
    worksheet.append(["Max charging rate", 2, "MW", ""])
    worksheet.append(["Max discharging rate", 2, "MW", ""])
    worksheet.append(["Max storage volume", 4, "MWh", ""])
    worksheet.append(["Battery charging efficiency", 0.05, "-", ""])
    worksheet.append(["Battery discharging efficiency", 0.05, "-", ""])

    path = tmp_path / "battery_parameters.xlsx"
    workbook.save(path)
    return path


@pytest.fixture
def market_prices_path(tmp_path):
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "Half-hourly data"
    worksheet.append([None, "Market 1 Price [£/MWh]"])
    worksheet.append([datetime(2018, 1, 1, 0, 0), 10.0])
    worksheet.append([datetime(2018, 1, 1, 0, 30), 200.0])

    path = tmp_path / "market_prices.xlsx"
    workbook.save(path)
    return path


def test_main_writes_a_dispatch_csv_and_prints_a_profit_summary(
    battery_parameters_path, market_prices_path, tmp_path, capsys
):
    output_csv_path = tmp_path / "dispatch.csv"

    main(battery_parameters_path, market_prices_path, output_csv_path)

    with open(output_csv_path, newline="") as csv_file:
        rows = list(csv.DictReader(csv_file))
    assert len(rows) == 2

    assert "Total profit" in capsys.readouterr().out
