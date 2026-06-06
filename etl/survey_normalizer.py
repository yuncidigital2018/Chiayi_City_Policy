"""Normalizer for city survey data (天下雜誌 + 遠見雜誌)."""
import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def normalize_cw_happy_city() -> pd.DataFrame | None:
    """Normalize 天下雜誌 永續幸福城市 data."""
    path = RAW_DIR / "cw_happy_city_2025.csv"
    if not path.exists():
        logger.warning("cw_happy_city_2025.csv not found")
        return None

    df = pd.read_csv(path, encoding="utf-8")
    df.columns = df.columns.str.strip()

    # Overall rankings
    rankings = df[df["group"].isin(["六都", "非六都"])].copy()
    rankings = rankings[["year", "group", "rank", "county", "total_score", "source"]].copy()
    rankings["rank"] = pd.to_numeric(rankings["rank"], errors="coerce").astype("Int64")
    rankings["total_score"] = pd.to_numeric(rankings["total_score"], errors="coerce")

    return rankings


def normalize_cw_dimensions() -> pd.DataFrame | None:
    """Normalize 天下雜誌 dimension scores."""
    path = RAW_DIR / "cw_happy_city_2025.csv"
    if not path.exists():
        return None

    df = pd.read_csv(path, encoding="utf-8")
    dims = df[df["group"] == "面向"].copy()
    if dims.empty:
        return None

    result = dims.rename(columns={"total_score": "score", "rank": "rank_in_non_six"})
    result = result[["year", "dimension", "county", "score", "rank_in_non_six", "note"]].copy()
    result["score"] = pd.to_numeric(result["score"], errors="coerce")
    result["rank_in_non_six"] = pd.to_numeric(result["rank_in_non_six"], errors="coerce").astype("Int64")

    return result


def normalize_gvm_satisfaction() -> pd.DataFrame | None:
    """Normalize 遠見雜誌 施政滿意度 data."""
    path = RAW_DIR / "gvm_mayor_satisfaction_2026.csv"
    if not path.exists():
        logger.warning("gvm_mayor_satisfaction_2026.csv not found")
        return None

    df = pd.read_csv(path, encoding="utf-8")
    df.columns = df.columns.str.strip()

    return df


def run_survey_normalization() -> dict[str, Path | None]:
    """Run all survey normalizers."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    results = {}

    # 天下 rankings
    cw_rankings = normalize_cw_happy_city()
    if cw_rankings is not None and not cw_rankings.empty:
        path = PROCESSED_DIR / "cw_happy_city_rankings.csv"
        cw_rankings.to_csv(path, index=False, encoding="utf-8")
        logger.info(f"Saved cw_happy_city_rankings → {path} ({len(cw_rankings)} rows)")
        results["cw_happy_city_rankings"] = path

    # 天下 dimensions
    cw_dims = normalize_cw_dimensions()
    if cw_dims is not None and not cw_dims.empty:
        path = PROCESSED_DIR / "cw_happy_city_dimensions.csv"
        cw_dims.to_csv(path, index=False, encoding="utf-8")
        logger.info(f"Saved cw_happy_city_dimensions → {path} ({len(cw_dims)} rows)")
        results["cw_happy_city_dimensions"] = path

    # 遠見 satisfaction
    gvm = normalize_gvm_satisfaction()
    if gvm is not None and not gvm.empty:
        path = PROCESSED_DIR / "gvm_mayor_satisfaction.csv"
        gvm.to_csv(path, index=False, encoding="utf-8")
        logger.info(f"Saved gvm_mayor_satisfaction → {path} ({len(gvm)} rows)")
        results["gvm_mayor_satisfaction"] = path

    return results
