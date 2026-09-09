import csv
from datetime import datetime

import pytest

from battery_optimizer.dispatch import Action, DispatchRecord
from battery_optimizer.summary import summarize, write_records_csv


def _record(action, power_megawatts, price, duration_hours=0.5):
    return DispatchRecord(
        period_start=datetime(2018, 1, 1),
        action=action,
        power_megawatts=power_megawatts,
        price_pounds_per_megawatt_hour=price,
        duration_hours=duration_hours,
        state_of_charge_megawatt_hours=0.0,
    )


def test_summarize_computes_profit_and_energy_totals():
    records = [
        _record(Action.IDLE, 0.0, 40.0),
        _record(Action.CHARGE, 2.0, 10.0),
        _record(Action.DISCHARGE, 2.0, 60.0),
    ]

    summary = summarize(records)

    expected_profit = -(2.0 * 0.5 * 10.0) + (2.0 * 0.5 * 60.0)
    assert summary.total_profit_pounds == pytest.approx(expected_profit)
    assert summary.total_energy_charged_megawatt_hours == pytest.approx(1.0)
    assert summary.total_energy_discharged_megawatt_hours == pytest.approx(1.0)


def test_write_records_csv_writes_a_header_and_one_row_per_record(tmp_path):
    records = [_record(Action.CHARGE, 2.0, 10.0)]
    csv_path = tmp_path / "dispatch.csv"

    write_records_csv(records, csv_path)

    with open(csv_path, newline="") as csv_file:
        rows = list(csv.DictReader(csv_file))

    assert len(rows) == 1
    assert rows[0]["action"] == "charge"
    assert rows[0]["power_megawatts"] == "2.0"
