"""
fetch_zillow_zhvi.py

Downloads Zillow's state-level Home Value Index (ZHVI) — a dataset Zillow
explicitly publishes for public reuse on its Research Data page
(https://www.zillow.com/research/data/), free, no login, no API key, no
scraping of rendered pages: it's a direct CSV download of data Zillow
intends third parties to use, with attribution ("Data ... provided by
Zillow" — see their research page for the exact attribution wording and
current terms before publishing anything derived from it).

This is the "legitimate public data source" version of a scraping task:
instead of parsing HTML off zillow.com (against their ToS) or hitting an
undocumented private endpoint, this hits the stable CSV export Zillow
maintains specifically for external use.

USAGE
    python3 fetch_zillow_zhvi.py

BEHAVIOR
    1. Tries the live download from Zillow's research file server.
    2. On any network failure (including sandboxed environments with no
       general internet egress), falls back to the bundled sample snapshot
       in data/cache/state_zhvi_sample.csv so the rest of the pipeline can
       still be demoed offline. The fallback is logged loudly so it's never
       silently mistaken for live data.

NOTE ON THE URL
    Zillow occasionally renames/re-versions these files. If this returns a
    404, go to https://www.zillow.com/research/data/, find "ZHVI All Homes
    (SFR, Condo/Co-op) Time Series ($) - State" under "Home Values", and
    copy the current CSV link into ZHVI_URL below.
"""
import sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

DATA_DIR = Path(__file__).resolve().parent / "data"
CACHE_DIR = DATA_DIR / "cache"
RAW_OUT = DATA_DIR / "state_zhvi_raw.csv"
SAMPLE_FALLBACK = CACHE_DIR / "state_zhvi_sample.csv"

ZHVI_URL = (
    "https://files.zillowstatic.com/research/public_csvs/zhvi/"
    "State_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv"
)
TIMEOUT_SECONDS = 20


def download(url: str, dest: Path) -> bool:
    req = Request(url, headers={"User-Agent": "portfolio-project/1.0 (data engineering demo)"})
    try:
        with urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(resp.read())
        return True
    except (URLError, HTTPError) as e:
        print(f"[warn] live download failed ({e}); will use cached sample instead.", file=sys.stderr)
        return False


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ok = download(ZHVI_URL, RAW_OUT)
    if ok:
        print(f"Downloaded live ZHVI data -> {RAW_OUT}")
        return RAW_OUT

    if not SAMPLE_FALLBACK.exists():
        raise SystemExit(
            "Live download failed and no cached sample is available. "
            "Check network access or update ZHVI_URL."
        )
    print(
        "[fallback] Using bundled SAMPLE data (data/cache/state_zhvi_sample.csv). "
        "This is illustrative, structurally-similar data for offline demo purposes "
        "only — it is NOT real Zillow data. Run this script with normal internet "
        "access to pull the live dataset."
    )
    return SAMPLE_FALLBACK


if __name__ == "__main__":
    path = main()
    print(f"\nUsing data file: {path}")
