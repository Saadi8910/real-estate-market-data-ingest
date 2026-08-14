"""
enrich_leads_with_market.py

Joins the lead pipeline's output (../real-estate-lead-pipeline/output/leads_scored.csv)
with this project's state-level ZHVI market data, adding a "how does this
lead's assessed value compare to its state's current market" signal.

This is the piece that ties the two portfolio projects together into one
story: "pipeline A extracts and scores leads; pipeline B enriches them with
external market context."
"""
from pathlib import Path
import pandas as pd

LEADS_CSV = Path(__file__).resolve().parent.parent.parent / "real-estate-lead-pipeline" / "output" / "leads_scored.csv"
ZHVI_TIDY_CSV = Path(__file__).resolve().parent.parent / "output" / "state_zhvi_tidy.csv"
OUT_PATH = Path(__file__).resolve().parent.parent / "output" / "leads_with_market_context.csv"


def main():
    if not LEADS_CSV.exists():
        raise SystemExit(
            f"Could not find {LEADS_CSV}. Run the lead pipeline project first "
            "(python3 main.py in real-estate-lead-pipeline/)."
        )
    leads = pd.read_csv(LEADS_CSV)
    zhvi = pd.read_csv(ZHVI_TIDY_CSV, parse_dates=["month"])

    latest_zhvi = (
        zhvi.sort_values("month")
        .groupby("state_code", as_index=False)
        .tail(1)[["state_code", "zhvi"]]
        .rename(columns={"zhvi": "state_current_zhvi"})
    )

    enriched = leads.merge(
        latest_zhvi, left_on="property_state", right_on="state_code", how="left"
    ).drop(columns=["state_code"])

    enriched["value_vs_state_market_pct"] = (
        (enriched["assessed_value"] - enriched["state_current_zhvi"])
        / enriched["state_current_zhvi"]
    ).round(3)

    enriched["priced_below_market"] = enriched["value_vs_state_market_pct"] < -0.05

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    enriched.to_csv(OUT_PATH, index=False)
    print(f"wrote {len(enriched)} enriched leads -> {OUT_PATH}")
    print(f"leads priced >5% below their state's current market value: "
          f"{enriched['priced_below_market'].sum()}")


if __name__ == "__main__":
    main()
