import os

from battery_optimizer.data.loaders import load_battery_spec, load_market_one_prices
from battery_optimizer.dispatch import simulate
from battery_optimizer.summary import summarize, write_records_csv

BATTERY_PARAMETERS_PATH = "data/raw/Attachment 1.xlsx"
MARKET_PRICES_PATH = "data/raw/Attachment 2.xlsx"
OUTPUT_CSV_PATH = "results/dispatch.csv"


def main(
    battery_parameters_path=BATTERY_PARAMETERS_PATH,
    market_prices_path=MARKET_PRICES_PATH,
    output_csv_path=OUTPUT_CSV_PATH,
) -> None:
    battery_spec = load_battery_spec(battery_parameters_path)
    price_points = load_market_one_prices(market_prices_path)

    records = simulate(battery_spec, price_points)

    os.makedirs(os.path.dirname(output_csv_path) or ".", exist_ok=True)
    write_records_csv(records, output_csv_path)

    summary = summarize(records)
    print(f"Total profit: £{summary.total_profit_pounds:,.2f}")
    print(f"Energy charged: {summary.total_energy_charged_megawatt_hours:,.2f} MWh")
    print(f"Energy discharged: {summary.total_energy_discharged_megawatt_hours:,.2f} MWh")
    print(f"Dispatch schedule written to {output_csv_path}")


if __name__ == "__main__":
    main()
