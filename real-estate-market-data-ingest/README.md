# Real Estate Market Data Ingest (Zillow Research Data)

A small, focused pipeline that pulls U.S. state-level home value data from
**Zillow's Research Data** — a dataset Zillow publishes specifically for
public reuse — and joins it onto the leads from the
[`real-estate-lead-pipeline`](../real-estate-lead-pipeline) project to add
market context ("is this lead priced below its state's current market
value?").

## Why this is a legitimate data source (not a ToS-violating scrape)

Zillow publishes ZHVI (Zillow Home Value Index) and several other datasets
as direct CSV downloads at **zillow.com/research/data/**, explicitly for
external use with attribution — no login, no scraping of rendered pages,
no bypassing of paywalls or bot protection. This project downloads that
published CSV directly via a simple HTTP GET, the same way you'd click the
download link on their site. If you publish anything built from this data,
check Zillow's research page for their current attribution wording first.

## Pipeline

```
fetch_zillow_zhvi.py      -> downloads the state-level ZHVI CSV (or falls
                              back to a bundled, clearly-labeled sample if
                              there's no internet access)
src/transform_zhvi.py     -> reshapes the wide (one-column-per-month) export
                              into tidy long format: state, month, zhvi
src/enrich_leads_with_market.py
                           -> joins tidy ZHVI onto ../real-estate-lead-pipeline's
                              leads_scored.csv, adding:
                                - state_current_zhvi
                                - value_vs_state_market_pct
                                - priced_below_market (>5% under state ZHVI)
```

## Run it

```bash
pip install -r requirements.txt
python3 fetch_zillow_zhvi.py          # downloads live data, or falls back to sample
python3 src/transform_zhvi.py         # -> output/state_zhvi_tidy.csv
python3 src/enrich_leads_with_market.py   # -> output/leads_with_market_context.csv
```

**Important**: `enrich_leads_with_market.py` expects the
`real-estate-lead-pipeline` project to sit as a **sibling folder** and to
have already been run (`python3 main.py` there), since it reads that
project's `output/leads_scored.csv`.

## About the sample fallback

This sandboxed build environment used to write this project has no general
internet access, so `fetch_zillow_zhvi.py` could not reach zillow.com while
this repo was built — it fell back to `data/cache/state_zhvi_sample.csv`,
which is **synthetic data generated to match Zillow's real column
structure**, not real Zillow figures. Run the script yourself on a machine
with normal internet access and it will pull the live file instead — no
code changes needed. The fallback is logged loudly at runtime specifically
so it's never mistaken for real data.

## Interview talking points

- Explain *why* this is a legitimate source (published-for-reuse CSV) vs.
  scraping rendered HTML off a site that prohibits it — shows you think
  about data-sourcing ethics/ToS, not just "can I get the bytes."
- The wide-to-long reshape (`melt`) is a very common real data-engineering
  step — most public time-series exports come in wide format and need to
  be tidied before they're useful in SQL or Power BI.
- The graceful network-failure fallback (with a loud, unambiguous label
  on the sample data) shows defensive engineering — a pipeline that fails
  silently into fabricated-looking data is worse than one that fails loudly.
