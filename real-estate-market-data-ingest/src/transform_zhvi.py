"""
transform_zhvi.py

Reshapes Zillow's wide ZHVI export (one column per month) into tidy
long format: one row per (state, month). Works unmodified on either the
live download or the bundled sample fallback, since both share the same
column structure.
"""
from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
OUT_PATH = Path(__file__).resolve().parent.parent / "output" / "state_zhvi_tidy.csv"

ID_COLS = ["RegionID", "SizeRank", "RegionName", "RegionType", "StateName"]


def load_raw() -> pd.DataFrame:
    live = DATA_DIR / "state_zhvi_raw.csv"
    sample = DATA_DIR / "cache" / "state_zhvi_sample.csv"
    path = live if live.exists() else sample
    if path == sample:
        print("[info] transforming the SAMPLE dataset (no live file found).")
    return pd.read_csv(path), path


def to_tidy(df: pd.DataFrame) -> pd.DataFrame:
    date_cols = [c for c in df.columns if c not in ID_COLS]
    tidy = df.melt(id_vars=ID_COLS, value_vars=date_cols,
                    var_name="month", value_name="zhvi")
    tidy["month"] = pd.to_datetime(tidy["month"])
    tidy = tidy.dropna(subset=["zhvi"]).sort_values(["StateName", "month"])
    tidy = tidy.rename(columns={"StateName": "state_code", "RegionName": "state_name"})
    return tidy[["state_code", "state_name", "month", "zhvi"]].reset_index(drop=True)


def main():
    raw, path = load_raw()
    tidy = to_tidy(raw)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    tidy.to_csv(OUT_PATH, index=False)
    print(f"source: {path}")
    print(f"wrote {len(tidy)} tidy rows -> {OUT_PATH}")
    latest = tidy.sort_values("month").groupby("state_code").tail(1)
    print("\nMost recent ZHVI by state:")
    print(latest[["state_code", "month", "zhvi"]].to_string(index=False))


if __name__ == "__main__":
    main()
