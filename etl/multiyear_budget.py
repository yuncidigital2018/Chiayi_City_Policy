"""Multi-year budget normalizer — handle historical RIDs for YoY comparison."""
import logging
import pandas as pd
from pathlib import Path

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

# Historical RID mapping (revenue, mapped by total amount analysis)
# 106年: ~11.6M, 107: ~12.1M, 108: ~12.9M, 109: ~13.5M, 
# 110: ~14.5M, 111: ~17.1M, 112: ~15.3M, 113: ~18.0M, 114: ~19.0M, 115: ~19.8M
REVENUE_RID_YEARS = {
    'e84f38bd-c1b6-4820-ad1d-1965f813901e': 106,
    '7444b658-c2bd-4105-a7fa-3f7a6f00ad9f': 107,
    'a7c8a7d4-46e9-486b-9b04-844f83cfe9d8': 108,
    '866fab02-42ae-4652-9785-6c2dad53239d': 109,
    '1cd62759-37b4-4a97-99da-d5383bacc2d8': 110,
    'f34992dd-d7fe-439f-a3e5-618b786d9590': 111,
    '123eea35-b2e2-453e-b987-59e424e72f5e': 112,
    '9a733eac-2142-4c4c-b767-851e7f65f560': 113,
    'cd37dcf5-c077-411f-b749-7e7c87a123c5': 114,
    '6adc9ce1-37d4-4bff-ae27-fea9dfb1f04b': 115,
}


def normalize_multiyear_revenue(raw_dir: Path | None = None) -> pd.DataFrame | None:
    """Combine all available revenue year files into one multi-year dataset."""
    raw_dir = raw_dir or RAW_DIR
    all_rows = []

    for filename in raw_dir.glob("budget_revenue_*.csv"):
        # Extract year from filename: budget_revenue_115.csv → 115
        try:
            year = int(filename.stem.split('_')[-1])
        except ValueError:
            continue

        try:
            df = pd.read_csv(filename, encoding="utf-8")
            df.columns = df.columns.str.strip()

            # Detect amount column
            amount_col = None
            for c in ["合計（千元）", "合計", "本年度預算數"]:
                if c in df.columns:
                    amount_col = c
                    break
            if not amount_col:
                continue

            # Only top-level (款 level)
            if "款" in df.columns:
                df_top = df[df["款"].notna() & (df["款"].astype(str).str.strip() != "")].copy()
            else:
                df_top = df.copy()

            name_col = None
            for c in ["科目名稱", "名稱及編號", "名稱"]:
                if c in df_top.columns:
                    name_col = c
                    break
            if not name_col:
                continue

            for _, row in df_top.iterrows():
                all_rows.append({
                    'fiscal_year': year,
                    'source_category': str(row[name_col]).strip(),
                    'amount': int(pd.to_numeric(row[amount_col], errors='coerce') or 0),
                })
        except Exception as e:
            logger.warning(f"Failed to parse {filename}: {e}")

    if not all_rows:
        return None

    result = pd.DataFrame(all_rows)
    result['amount'] = pd.to_numeric(result['amount'], errors='coerce').fillna(0).astype('int64')
    return result


def create_revenue_trend(multiyear_df: pd.DataFrame | None) -> pd.DataFrame | None:
    """Create a trend table: fiscal_year → total revenue."""
    if multiyear_df is None or multiyear_df.empty:
        return None

    # Sum by year (only L1 items to avoid double counting)
    yearly = multiyear_df.groupby('fiscal_year')['amount'].sum().reset_index()
    yearly.columns = ['fiscal_year', 'total_revenue']
    yearly = yearly.sort_values('fiscal_year')

    # Add YoY change
    yearly['yoy_change'] = yearly['total_revenue'].diff()
    yearly['yoy_pct'] = yearly['total_revenue'].pct_change() * 100

    return yearly
