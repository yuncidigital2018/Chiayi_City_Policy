"""Data Normalizer — clean, standardize, and merge raw data into processed tables."""
import logging
from pathlib import Path
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

# ========================
# Schema definitions
# ========================

SCHEMA_POPULATION_ANNUAL = {
    "year": "int64",
    "total_population": "int64",
    "male": "int64",
    "female": "int64",
    "natural_increase": "int64",
    "social_increase": "int64",
}

SCHEMA_POPULATION_VILLAGE = {
    "year": "int64",
    "month": "int64",
    "district": "string",
    "village": "string",
    "households": "int64",
    "population": "int64",
}

SCHEMA_BUDGET_REVENUE = {
    "fiscal_year": "int64",
    "source_category": "string",
    "amount": "float64",
}

SCHEMA_BUDGET_EXPENDITURE_FUNCTION = {
    "fiscal_year": "int64",
    "function_category": "string",
    "amount": "float64",
}

SCHEMA_BUDGET_EXPENDITURE_AGENCY = {
    "fiscal_year": "int64",
    "agency_name": "string",
    "amount": "float64",
}


def _clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Strip whitespace from column names."""
    df.columns = df.columns.str.strip()
    return df


def _convert_schema(df: pd.DataFrame, schema: dict[str, str]) -> pd.DataFrame:
    """Apply schema types with safe conversion."""
    for col, dtype in schema.items():
        if col in df.columns:
            try:
                if "int" in dtype:
                    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype("int64")
                elif "float" in dtype:
                    df[col] = pd.to_numeric(df[col], errors="coerce")
                elif "string" in dtype:
                    df[col] = df[col].astype("string")
            except Exception as e:
                logger.warning(f"Column {col}: conversion to {dtype} failed: {e}")
    return df


# ========================
# Population normalizers
# ========================

def normalize_population_annual(raw_path: Path | str | None) -> pd.DataFrame | None:
    """Normalize yearly population data into PopulationAnnual schema."""
    if raw_path is None or not Path(raw_path).exists():
        logger.warning("population_annual: no raw data found")
        return None

    df = pd.read_csv(raw_path, encoding="utf-8")
    df = _clean_column_names(df)

    # Map columns to standard schema
    col_map = {}
    for col in df.columns:
        c = col.strip()
        if c == "年度":
            col_map[col] = "year"
        elif c == "總人口":
            col_map[col] = "total_population"
        elif c == "男性":
            col_map[col] = "male"
        elif c == "女性":
            col_map[col] = "female"
        elif c == "自然增減":
            col_map[col] = "natural_increase"
        elif c == "社會增減":
            col_map[col] = "social_increase"

    df = df.rename(columns=col_map)
    # Keep only standard columns
    standard_cols = ["year", "total_population", "male", "female", "natural_increase", "social_increase"]
    df = df[[c for c in standard_cols if c in df.columns]]
    df = _convert_schema(df, SCHEMA_POPULATION_ANNUAL)
    return df


def normalize_population_village(raw_path: Path | str | None) -> pd.DataFrame | None:
    """Normalize village-level monthly population data."""
    if raw_path is None or not Path(raw_path).exists():
        logger.warning("population_village: no raw data found")
        return None

    df = pd.read_csv(raw_path, encoding="utf-8")
    df = _clean_column_names(df)

    col_map = {}
    for col in df.columns:
        c = col.strip()
        if c == "年度":
            col_map[col] = "year"
        elif c == "月份":
            col_map[col] = "month"
        elif c in ("行政區", "區"):
            col_map[col] = "district"
        elif c in ("村里別", "里"):
            col_map[col] = "village"
        elif c == "戶數":
            col_map[col] = "households"
        elif c == "人口數":
            col_map[col] = "population"

    df = df.rename(columns=col_map)
    standard_cols = ["year", "month", "district", "village", "households", "population"]
    df = df[[c for c in standard_cols if c in df.columns]]
    df = _convert_schema(df, SCHEMA_POPULATION_VILLAGE)
    return df


# ========================
# Budget normalizers
# ========================

def normalize_budget_revenue(raw_path: Path | str | None, fiscal_year: int = 115) -> pd.DataFrame | None:
    """Normalize revenue-by-source budget data."""
    if raw_path is None or not Path(raw_path).exists():
        logger.warning("budget_revenue: no raw data found")
        return None

    df = pd.read_csv(raw_path, encoding="utf-8")
    df = _clean_column_names(df)

    # Map: keep only top-level categories (款 level, no sub-items)
    # Skip rows where 款 is empty (those are sub-items)
    df = df[df["款"].notna() & (df["款"].astype(str).str.strip() != "")].copy()

    result = pd.DataFrame({
        "fiscal_year": [fiscal_year] * len(df),
        "source_category": df["名稱及編號"].str.strip().values,
        "amount": pd.to_numeric(df["本年度預算數"], errors="coerce").fillna(0).values,
    })

    result = _convert_schema(result, SCHEMA_BUDGET_REVENUE)
    return result


def normalize_budget_expenditure_function(raw_path: Path | str | None, fiscal_year: int = 115) -> pd.DataFrame | None:
    """Normalize expenditure-by-function (政事別) budget data."""
    if raw_path is None or not Path(raw_path).exists():
        logger.warning("budget_expenditure_function: no raw data found")
        return None

    df = pd.read_csv(raw_path, encoding="utf-8")
    df = _clean_column_names(df)

    # Keep only top-level categories (款 level)
    df = df[df["款"].notna() & (df["款"].astype(str).str.strip() != "") &
            (df["項"].isna() | (df["項"].astype(str).str.strip() == ""))].copy()

    result = pd.DataFrame({
        "fiscal_year": [fiscal_year] * len(df),
        "function_category": df["名稱"].str.strip().values,
        "amount": pd.to_numeric(df["合計金額"], errors="coerce").fillna(0).values,
    })

    result = _convert_schema(result, SCHEMA_BUDGET_EXPENDITURE_FUNCTION)
    return result


def normalize_budget_expenditure_agency(raw_path: Path | str | None, fiscal_year: int = 115) -> pd.DataFrame | None:
    """Normalize expenditure-by-agency (機關別) budget data."""
    if raw_path is None or not Path(raw_path).exists():
        logger.warning("budget_expenditure_agency: no raw data found")
        return None

    df = pd.read_csv(raw_path, encoding="utf-8")
    df = _clean_column_names(df)

    result = pd.DataFrame({
        "fiscal_year": [fiscal_year] * len(df),
        "agency_name": df["名稱"].str.strip().values,
        "amount": pd.to_numeric(df["合計金額"], errors="coerce").fillna(0).values,
    })

    result = _convert_schema(result, SCHEMA_BUDGET_EXPENDITURE_AGENCY)
    return result


# ========================
# Orchestrator
# ========================

NORMALIZER_MAP = {
    "population_annual": (normalize_population_annual, "population_annual", {}),
    "population_village_monthly": (normalize_population_village, "population_village_monthly", {}),
    "budget_revenue_by_source": (normalize_budget_revenue, "budget_revenue_115", {"fiscal_year": 115}),
    "budget_expenditure_by_function": (normalize_budget_expenditure_function, "budget_expenditure_policy_115", {"fiscal_year": 115}),
    "budget_expenditure_by_agency": (normalize_budget_expenditure_agency, "budget_expenditure_dept_115", {"fiscal_year": 115}),
}


def run_normalization(raw_paths: dict[str, Path] | None = None) -> dict[str, Path]:
    """Run all normalizers and save processed CSVs."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    results = {}

    for table_name, (normalizer_fn, raw_filename, kwargs) in NORMALIZER_MAP.items():
        # Find raw data
        if raw_paths and raw_filename in raw_paths:
            raw_path = raw_paths[raw_filename]
        else:
            raw_path = RAW_DIR / f"{raw_filename}.csv"
            if not raw_path.exists():
                raw_path = None

        logger.info(f"Normalizing {table_name} (raw={raw_path})...")
        df = normalizer_fn(raw_path, **kwargs)

        if df is not None and not df.empty:
            output_path = PROCESSED_DIR / f"{table_name}.csv"
            df.to_csv(output_path, index=False, encoding="utf-8")
            logger.info(f"Saved {table_name} → {output_path} ({len(df)} rows)")
            results[table_name] = output_path
        else:
            logger.warning(f"Normalization produced empty result for {table_name}")
            results[table_name] = None

    return results
