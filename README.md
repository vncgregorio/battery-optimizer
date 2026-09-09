# Battery Optimizer

A small Python package that simulates a battery charging and discharging in a
wholesale electricity market to earn a profit, using the price and battery data
supplied for this exercise.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Running it

```bash
python -m battery_optimizer.cli
```

This reads `data/raw/Attachment 1.xlsx` (battery parameters) and
`data/raw/Attachment 2.xlsx` (market prices), runs the dispatch simulation over the
full three years of half-hourly Market 1 data, prints a profit summary, and writes the
full half-hourly schedule to `results/dispatch.csv`.

## Running the tests

```bash
pip install -e ".[dev]"
pytest
```

## Results

Running the model against the supplied data produces:

```
Total profit: £22,576.75
Energy charged: 624.80 MWh
Energy discharged: 563.88 MWh
```

## Approach

The battery decides what to do in each half-hour purely from Market 1's price: two
fixed thresholds (the 20th and 80th percentile of the full three-year price series) are
computed up front, and the battery charges at its maximum sustainable rate whenever the
price is below the cheap threshold, discharges whenever it's above the expensive
threshold, and sits idle otherwise; the rate is always capped by whichever binds first,
the battery's rated power or its remaining stored energy/headroom. Market 2 and the
other supplied battery parameters (capex, lifetime, degradation) were reviewed but left
out of the model to keep the exercise focused and within its intended scope — the brief
explicitly allows focusing on a single market and using simple, non-optimal decision
logic, and Market 1's finer half-hourly granularity made it the more natural one to
model.
