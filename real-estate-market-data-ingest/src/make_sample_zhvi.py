"""
make_sample_zhvi.py

Generates data/cache/state_zhvi_sample.csv — a SYNTHETIC fallback used only
when fetch_zillow_zhvi.py cannot reach the live internet (e.g. this
sandboxed build environment). It mirrors the exact column structure of
Zillow's real state-level ZHVI export (RegionID, SizeRank, RegionName,
RegionType, StateName, then one column per month) so downstream code
(transform_zhvi.py) works unmodified against either file.

THE VALUES BELOW ARE MADE UP. They are shaped to be directionally
realistic (plausible home-value levels and month-over-month growth) but
must never be presented as real Zillow figures — they exist purely so the
pipeline is runnable and demonstrable without live internet access.
"""
import random
from pathlib import Path
import pandas as pd

random.seed(7)

OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "cache" / "state_zhvi_sample.csv"

# States matching the ones used in the lead-pipeline project, so the two
# projects can be joined together in enrich_leads_with_market.py
STATES = {
    "Texas": ("TX", 310_000),
    "Florida": ("FL", 385_000),
    "Georgia": ("GA", 330_000),
    "North Carolina": ("NC", 340_000),
    "Arizona": ("AZ", 415_000),
    "Ohio": ("OH", 225_000),
    "Tennessee": ("TN", 345_000),
    "Nevada": ("NV", 420_000),
}

N_MONTHS = 24


def month_columns(n):
    start = pd.Timestamp(2024, 8, 1)
    periods = pd.date_range(start=start, periods=n, freq="ME")
    return [d.strftime("%Y-%m-%d") for d in periods]


def main():
    cols = month_columns(N_MONTHS)
    rows = []
    for region_id, (state_name, (abbr, base_value)) in enumerate(STATES.items(), start=1):
        row = {
            "RegionID": 1000 + region_id,
            "SizeRank": region_id,
            "RegionName": state_name,
            "RegionType": "state",
            "StateName": abbr,
        }
        value = base_value
        for c in cols:
            drift = random.uniform(-0.004, 0.012)  # roughly flat-to-rising, like recent US trend
            value = value * (1 + drift)
            row[c] = round(value, 0)
        rows.append(row)

    df = pd.DataFrame(rows)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_PATH, index=False)
    print(f"wrote SAMPLE (synthetic, not real Zillow data) -> {OUT_PATH}")


if __name__ == "__main__":
    main()
