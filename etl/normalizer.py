"""Data Normalizer — clean, standardize, and merge raw data into processed tables."""
import logging
import re
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
    "households": "int64",
    "growth_pct": "string",
}

SCHEMA_POPULATION_AGE_GENDER = {
    "age_group": "string",
    "male": "int64",
    "female": "int64",
    "total": "int64",
    "age_midpoint": "float64",
}

SCHEMA_POPULATION_VILLAGE = {
    "year": "int64",
    "month": "int64",
    "district": "string",
    "village": "string",
    "households": "int64",
    "male": "int64",
    "female": "int64",
    "population": "int64",
}

SCHEMA_BUDGET_REVENUE = {
    "fiscal_year": "int64",
    "source_category": "string",
    "amount": "float64",
}

SCHEMA_BUDGET_EXPENDITURE_FUNCTION = {
    "fiscal_year": "int64",
    "level": "int64",
    "parent_code": "string",
    "code": "string",
    "function_category": "string",
    "recurring": "float64",
    "capital": "float64",
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
    """Normalize yearly population data (from household scraper).
    
    Supports scraper columns: year, households, male, female, total, growth_pct
    Maps to standard schema: year, total_population, male, female, households, growth_pct
    """
    if raw_path is None or not Path(raw_path).exists():
        logger.warning("population_annual: no raw data found")
        return None

    df = pd.read_csv(raw_path, encoding="utf-8")
    df = _clean_column_names(df)

    col_map = {}
    for col in df.columns:
        c = col.strip()
        if c == "年度":
            col_map[col] = "year"
        elif c in ("總人口", "total"):
            col_map[col] = "total_population"
        elif c == "male":
            col_map[col] = "male"
        elif c == "female":
            col_map[col] = "female"
        elif c == "households":
            col_map[col] = "households"
        elif c == "growth_pct":
            col_map[col] = "growth_pct"

    df = df.rename(columns=col_map)

    # Map 'total' to 'total_population' if not already mapped
    if "total" in df.columns and "total_population" not in df.columns:
        df = df.rename(columns={"total": "total_population"})

    standard_cols = ["year", "total_population", "male", "female", "natural_increase",
                     "social_increase", "households", "growth_pct"]
    df = df[[c for c in standard_cols if c in df.columns]]
    df = _convert_schema(df, SCHEMA_POPULATION_ANNUAL)
    return df


def _parse_age_midpoint(age_group: str) -> float:
    """Convert age group like '0~4歲' to midpoint (2.0)."""
    m = re.match(r'(\d+)~(\d+)歲', age_group)
    if m:
        return (int(m.group(1)) + int(m.group(2))) / 2.0
    m2 = re.match(r'(\d+)歲', age_group)
    if m2:
        return float(m2.group(1))
    return 0.0


def normalize_population_age_gender(raw_path: Path | str | None) -> pd.DataFrame | None:
    """Normalize age/gender population data (population pyramid)."""
    if raw_path is None or not Path(raw_path).exists():
        logger.warning("population_age_gender: no raw data found")
        return None

    df = pd.read_csv(raw_path, encoding="utf-8")
    df = _clean_column_names(df)

    for col in ["age_group", "male", "female", "total"]:
        if col not in df.columns:
            logger.warning(f"population_age_gender: missing column {col}")
            return None

    df = _convert_schema(df, SCHEMA_POPULATION_AGE_GENDER)
    df["age_midpoint"] = df["age_group"].apply(_parse_age_midpoint)
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
        elif c == "人口數" or c == "population":
            col_map[col] = "population"
        elif c == "male":
            col_map[col] = "male"
        elif c == "female":
            col_map[col] = "female"

    df = df.rename(columns=col_map)
    standard_cols = ["year", "month", "district", "village", "households", "male", "female", "population"]
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

    name_col = None
    for candidate in ["科目名稱", "名稱及編號", "名稱"]:
        if candidate in df.columns:
            name_col = candidate
            break
    if name_col is None:
        logger.error(f"budget_revenue: cannot find name column. Available: {list(df.columns)}")
        return None

    amount_col = None
    for candidate in ["合計（千元）", "合計", "本年度預算數"]:
        if candidate in df.columns:
            amount_col = candidate
            break
    if amount_col is None:
        logger.error(f"budget_revenue: cannot find amount column. Available: {list(df.columns)}")
        return None

    df_top = df[df["款"].notna() & (df["款"].astype(str).str.strip() != "")].copy()

    result = pd.DataFrame({
        "fiscal_year": [fiscal_year] * len(df_top),
        "source_category": df_top[name_col].str.strip().values,
        "amount": pd.to_numeric(df_top[amount_col], errors="coerce").fillna(0).values,
    })

    result = _convert_schema(result, SCHEMA_BUDGET_REVENUE)
    return result


def normalize_budget_expenditure_function(raw_path: Path | str | None, fiscal_year: int = 115) -> pd.DataFrame | None:
    """Normalize expenditure-by-function (政事別) with L1/L2 hierarchy."""
    if raw_path is None or not Path(raw_path).exists():
        logger.warning("budget_expenditure_function: no raw data found")
        return None

    df = pd.read_csv(raw_path, encoding="utf-8")
    df = _clean_column_names(df)

    rows = []
    current_parent = None

    for _, row in df.iterrows():
        kuan_raw = row.get("款", None)
        xiang_raw = row.get("項", None)
        kuan = str(kuan_raw).strip() if pd.notna(kuan_raw) else ""
        xiang = str(xiang_raw).strip() if pd.notna(xiang_raw) else ""
        name = str(row.get("名稱", "")).strip()
        recurring = pd.to_numeric(row.get("經常門", 0), errors="coerce") if pd.notna(row.get("經常門")) else 0
        capital = pd.to_numeric(row.get("資本門", 0), errors="coerce") if pd.notna(row.get("資本門")) else 0
        total = pd.to_numeric(row.get("合計金額", 0), errors="coerce") if pd.notna(row.get("合計金額")) else 0

        if kuan and not xiang:
            current_parent = kuan
            rows.append({
                "fiscal_year": fiscal_year,
                "level": 1,
                "parent_code": kuan,
                "code": "",
                "function_category": name,
                "recurring": recurring,
                "capital": capital,
                "amount": total,
            })
        elif kuan and xiang:
            rows.append({
                "fiscal_year": fiscal_year,
                "level": 2,
                "parent_code": current_parent or kuan,
                "code": xiang,
                "function_category": name,
                "recurring": recurring,
                "capital": capital,
                "amount": total,
            })
        elif not kuan and xiang:
            rows.append({
                "fiscal_year": fiscal_year,
                "level": 2,
                "parent_code": current_parent or "",
                "code": xiang,
                "function_category": name,
                "recurring": recurring,
                "capital": capital,
                "amount": total,
            })

    result = pd.DataFrame(rows)
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
    "population_annual": (normalize_population_annual, "population_historical", {}),
    "population_age_gender": (normalize_population_age_gender, "population_age_gender", {}),
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
