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
    "level": "int64",           # 1=款(top), 2=項(sub)
    "parent_code": "string",     # 款 code (e.g. "01")
    "code": "string",            # 項 code (e.g. "01", "02") or empty for 款
    "function_category": "string",
    "recurring": "float64",      # 經常門
    "capital": "float64",        # 資本門
    "amount": "float64",         # 合計
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
    """Normalize revenue-by-source budget data.
    
    Handles both sample format (名稱及編號/本年度預算數) and
    real Open Chiayi format (科目名稱/合計（千元）).
    """
    if raw_path is None or not Path(raw_path).exists():
        logger.warning("budget_revenue: no raw data found")
        return None

    df = pd.read_csv(raw_path, encoding="utf-8")
    df = _clean_column_names(df)

    # Detect column names: real vs sample format
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

    # Keep only top-level categories (款 level, skip sub-items where 款 is empty)
    df_top = df[df["款"].notna() & (df["款"].astype(str).str.strip() != "")].copy()

    result = pd.DataFrame({
        "fiscal_year": [fiscal_year] * len(df_top),
        "source_category": df_top[name_col].str.strip().values,
        "amount": pd.to_numeric(df_top[amount_col], errors="coerce").fillna(0).values,
    })

    result = _convert_schema(result, SCHEMA_BUDGET_REVENUE)
    return result


def normalize_budget_expenditure_function(raw_path: Path | str | None, fiscal_year: int = 115) -> pd.DataFrame | None:
    """Normalize expenditure-by-function (政事別) budget data.
    
    Outputs both L1 (款) and L2 (項) rows with parent_code for drill-down.
    """
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
            # L1: top-level category (款)
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
            # L2: sub-category (項) under current parent
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
            # L2: sub-category with missing 款 (fall back to current_parent)
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
