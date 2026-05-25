"""Cross-county population comparison — fetch from 內政部戶政司 open data API.

API: https://www.ris.gov.tw/rs-opendata/api/v1/datastore/ODRP048/{year}
Returns: site_id, people_total, area, population_density for all 鄉鎮市區 nationwide.
"""
import logging
import re
from pathlib import Path
from typing import Any

import pandas as pd
import requests

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

API_BASE = "https://www.ris.gov.tw/rs-opendata/api/v1/datastore/ODRP048"

# 22 counties in Taiwan (ordered by traditional administrative ranking)
COUNTY_ORDER = [
    "臺北市", "新北市", "桃園市", "臺中市", "臺南市", "高雄市",
    "新竹縣", "苗栗縣", "彰化縣", "南投縣", "雲林縣", "嘉義縣",
    "屏東縣", "宜蘭縣", "花蓮縣", "臺東縣", "澎湖縣",
    "基隆市", "新竹市", "嘉義市",
    "金門縣", "連江縣",
]


def extract_county(site_id: str) -> str | None:
    """Extract county name from site_id like '嘉義市東區' → '嘉義市'."""
    m = re.match(r'^(.+?[市縣])', site_id)
    return m.group(1) if m else None


def fetch_county_population(year: int = 114, max_retries: int = 3) -> list[dict] | None:
    """Fetch nationwide township population data from 內政部 API."""
    import time

    url = f"{API_BASE}/{year}"
    last_error = None

    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            data = resp.json()

            if data.get("responseCode") != "OD-0101-S":
                logger.error(f"API error: {data.get('responseMessage')}")
                return None

            return data.get("responseData", [])
        except Exception as e:
            last_error = e
            if attempt < max_retries:
                wait = 2 ** attempt
                logger.warning(f"Attempt {attempt} failed ({e}), retry in {wait}s...")
                time.sleep(wait)

    logger.error(f"All {max_retries} attempts failed: {last_error}")
    return None


def normalize_county_comparison(raw_data: list[dict] | None = None, year: int = 114) -> pd.DataFrame | None:
    """Aggregate township data to county level for comparison.

    Returns DataFrame with columns:
    - county, population, area_km2, density, year
    """
    if raw_data is None:
        return None

    rows = []
    for item in raw_data:
        site_id = item.get("site_id", "")
        county = extract_county(site_id)
        if not county:
            continue
        rows.append({
            "county": county,
            "population": int(item.get("people_total", 0)),
            "area_km2": float(item.get("area", 0)),
        })

    df = pd.DataFrame(rows)
    if df.empty:
        return None

    # Aggregate by county
    agg = df.groupby("county").agg(
        population=("population", "sum"),
        area_km2=("area_km2", "sum"),
    ).reset_index()

    agg["density"] = (agg["population"] / agg["area_km2"]).round(1)
    agg["year"] = year

    # Sort by population descending
    agg = agg.sort_values("population", ascending=False).reset_index(drop=True)

    # Add rank
    agg["rank"] = range(1, len(agg) + 1)

    # Reorder columns
    agg = agg[["rank", "county", "year", "population", "area_km2", "density"]]

    return agg


def run_cross_county_pipeline(years: list[int] | None = None) -> pd.DataFrame | None:
    """Fetch and normalize county comparison data for multiple years."""
    if years is None:
        years = [114]

    all_dfs = []
    for year in years:
        logger.info(f"Fetching county population for year {year}...")
        raw = fetch_county_population(year)
        if raw:
            df = normalize_county_comparison(raw, year)
            if df is not None:
                all_dfs.append(df)
                logger.info(f"  Year {year}: {len(df)} counties")
        else:
            logger.warning(f"  Year {year}: no data")

    if not all_dfs:
        return None

    result = pd.concat(all_dfs, ignore_index=True)

    # Save
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    output_path = PROCESSED_DIR / "county_population_comparison.csv"
    result.to_csv(output_path, index=False, encoding="utf-8")
    logger.info(f"Saved county comparison → {output_path} ({len(result)} rows)")

    return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    df = run_cross_county_pipeline([114])
    if df is not None:
        # Show Chiayi City rank
        chiayi = df[df["county"] == "嘉義市"]
        if not chiayi.empty:
            print(f"\n嘉義市排名: 第 {chiayi.iloc[0]['rank']}/{len(df)} 名")
            print(f"人口: {chiayi.iloc[0]['population']:,}")
            print(f"密度: {chiayi.iloc[0]['density']}")
