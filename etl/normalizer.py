"""Data Normalizer — clean, standardize, and merge raw data into processed tables."""
import logging
from pathlib import Path
from typing import Any

import pandas as pd

from etl.config_loader import load_datasources, get_source_by_id

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
    """Strip whitespace from column names and standardize."""
    df.columns = df.columns.str.strip()
    return df


def _convert_schema(df: pd.DataFrame, schema: dict[str, str]) -> pd.DataFrame:
    """Apply schema types to a DataFrame, with safe conversion."""
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

    # Map columns (adjust based on actual source columns)
    col_map = {}
    for col in df.columns:
        if "年度" in col or "年" == col.strip():
            col_map[col] = "year"
        elif "總計" in col or "總人口" in col:
            col_map[col] = "total_population"
        elif "男" in col and "人口" in col:
            col_map[col] = "male"
        elif "女" in col and "人口" in col:
            col_map[col] = "female"
        elif "自然" in col:
            col_map[col] = "natural_increase"
        elif "社會" in col:
            col_map[col] = "social_increase"

    df = df.rename(columns=col_map)
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
        if "年" in col and len(col.strip()) <= 4:
            col_map[col] = "year"
        elif "月" in col:
            col_map[col] = "month"
        elif "區" in col or "行政區" in col:
            col_map[col] = "district"
        elif "里" in col:
            col_map[col] = "village"
        elif "戶" in col:
            col_map[col] = "households"
        elif "人口" in col or "人" in col:
            col_map[col] = "population"

    df = df.rename(columns=col_map)
    df = _convert_schema(df, SCHEMA_POPULATION_VILLAGE)
    return df


# ========================
# Budget normalizers
# ========================

def normalize_budget_revenue(raw_path: Path | str | None) -> pd.DataFrame | None:
    """Normalize revenue-by-source budget data."""
    if raw_path is None or not Path(raw_path).exists():
        logger.warning("budget_revenue: no raw data found")
        return None

    df = pd.read_csv(raw_path, encoding="utf-8")
    df = _clean_column_names(df)

    col_map = {}
    for col in df.columns:
        if "年度" in col or "會計" in col:
            col_map[col] = "fiscal_year"
        elif "來源" in col or "類別" in col or "科目" in col:
            col_map[col] = "source_category"
        elif "預算" in col or "金額" in col or "數" in col:
            col_map[col] = "amount"

    df = df.rename(columns=col_map)
    df = _convert_schema(df, SCHEMA_BUDGET_REVENUE)
    return df


def normalize_budget_expenditure_function(raw_path: Path | str | None) -> pd.DataFrame | None:
    """Normalize expenditure-by-function (政事別) budget data."""
    if raw_path is None or not Path(raw_path).exists():
        logger.warning("budget_expenditure_function: no raw data found")
        return None

    df = pd.read_csv(raw_path, encoding="utf-8")
    df = _clean_column_names(df)

    col_map = {}
    for col in df.columns:
        if "年度" in col:
            col_map[col] = "fiscal_year"
        elif "政事" in col or "功能" in col or "類別" in col:
            col_map[col] = "function_category"
        elif "預算" in col or "金額" in col or "數" in col:
            col_map[col] = "amount"

    df = df.rename(columns=col_map)
    df = _convert_schema(df, SCHEMA_BUDGET_EXPENDITURE_FUNCTION)
    return df


def normalize_budget_expenditure_agency(raw_path: Path | str | None) -> pd.DataFrame | None:
    """Normalize expenditure-by-agency (機關別) budget data."""
    if raw_path is None or not Path(raw_path).exists():
        logger.warning("budget_expenditure_agency: no raw data found")
        return None

    df = pd.read_csv(raw_path, encoding="utf-8")
    df = _clean_column_names(df)

    col_map = {}
    for col in df.columns:
        if "年度" in col:
            col_map[col] = "fiscal_year"
        elif "機關" in col or "單位" in col:
            col_map[col] = "agency_name"
        elif "預算" in col or "金額" in col or "數" in col:
            col_map[col] = "amount"

    df = df.rename(columns=col_map)
    df = _convert_schema(df, SCHEMA_BUDGET_EXPENDITURE_AGENCY)
    return df


# ========================
# Orchestrator
# ========================

# Mapping from logical table name to (normalizer function, source_id)
NORMALIZER_MAP = {
    "population_annual": (normalize_population_annual, None),
    "population_village_monthly": (normalize_population_village, None),
    "budget_revenue_by_source": (normalize_budget_revenue, "budget_revenue"),
    "budget_expenditure_by_function": (normalize_budget_expenditure_function, "budget_expenditure_policy"),
    "budget_expenditure_by_agency": (normalize_budget_expenditure_agency, "budget_expenditure_dept"),
}


def run_normalization(raw_paths: dict[str, Path] | None = None) -> dict[str, Path]:
    """Run all normalizers and save processed CSVs.

    Args:
        raw_paths: Dict mapping source_id → raw file path (from fetcher)

    Returns:
        Dict mapping table_name → processed file path
    """
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    results = {}

    for table_name, (normalizer_fn, source_id) in NORMALIZER_MAP.items():
        # Find raw data
        if raw_paths and source_id and source_id in raw_paths:
            raw_path = raw_paths[source_id]
        else:
            # Search raw directory for matching file
            raw_path = _find_raw_file(table_name)

        logger.info(f"Normalizing {table_name} (raw={raw_path})...")
        df = normalizer_fn(raw_path)

        if df is not None and not df.empty:
            output_path = PROCESSED_DIR / f"{table_name}.csv"
            df.to_csv(output_path, index=False, encoding="utf-8")
            logger.info(f"Saved {table_name} → {output_path} ({len(df)} rows)")
            results[table_name] = output_path
        else:
            logger.warning(f"Normalization produced empty result for {table_name}")
            results[table_name] = None

    return results


def _find_raw_file(table_name: str) -> Path | None:
    """Search raw directory for a matching CSV file."""
    if not RAW_DIR.exists():
        return None
    for f in RAW_DIR.iterdir():
        if f.suffix == ".csv" and table_name.split("_")[0] in f.stem:
            return f
    return None
