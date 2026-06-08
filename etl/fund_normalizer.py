"""Fund data normalizer — normalize 作業/營業/政事型基金綜計表."""
from __future__ import annotations

import logging
import pandas as pd
from pathlib import Path

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def normalize_fund_operating(raw_path: Path | str | None) -> pd.DataFrame | None:
    """Normalize 作業基金綜計表.
    
    Format: 科目, 合計 金額, 合計 ％, [各基金 金額, 各基金 ％], ...
    """
    if raw_path is None or not Path(raw_path).exists():
        logger.warning("fund_operating: no raw data found")
        return None

    df = pd.read_csv(raw_path, encoding="utf-8")
    df.columns = df.columns.str.strip()

    # Extract fund names from columns (pairs of 金額 and ％)
    fund_cols = [c for c in df.columns if c not in ['科目', '合計 金額', '合計 ％']]
    fund_names = list(set(c.replace(' 金額', '').replace(' ％', '') for c in fund_cols if '金額' in c or '％' in c))

    rows = []
    for _, row in df.iterrows():
        item = str(row.get('科目', '')).strip()
        if not item or item.startswith('合計'):
            continue
        total = pd.to_numeric(row.get('合計 金額', 0), errors='coerce')
        if pd.isna(total) or total == 0:
            continue
        rows.append({
            'fund_type': '作業基金',
            'item': item,
            'fund_name': '合計',
            'amount': int(total),
        })

    result = pd.DataFrame(rows)
    if not result.empty:
        result['amount'] = pd.to_numeric(result['amount'], errors='coerce').fillna(0).astype('int64')
    return result


def normalize_fund_business(raw_path: Path | str | None) -> pd.DataFrame | None:
    """Normalize 營業基金綜計表.
    
    Format: 科目, 合計, [各公司], ...
    """
    if raw_path is None or not Path(raw_path).exists():
        logger.warning("fund_business: no raw data found")
        return None

    df = pd.read_csv(raw_path, encoding="utf-8")
    df.columns = df.columns.str.strip()

    rows = []
    for _, row in df.iterrows():
        item = str(row.get('科目', '')).strip()
        total = pd.to_numeric(row.get('合計', 0), errors='coerce')
        if pd.isna(total) or total == 0:
            continue
        rows.append({
            'fund_type': '營業基金',
            'item': item,
            'fund_name': '合計',
            'amount': int(total),
        })

        # Also extract per-company data
        for col in df.columns:
            if col not in ['科目', '合計'] and pd.notna(row.get(col)):
                val = pd.to_numeric(row[col], errors='coerce')
                if not pd.isna(val) and val > 0:
                    rows.append({
                        'fund_type': '營業基金',
                        'item': item,
                        'fund_name': col,
                        'amount': int(val),
                    })

    result = pd.DataFrame(rows)
    if not result.empty:
        result['amount'] = pd.to_numeric(result['amount'], errors='coerce').fillna(0).astype('int64')
    return result


def normalize_fund_affairs(raw_path: Path | str | None) -> pd.DataFrame | None:
    """Normalize 政事型基金預算.
    
    Format: 基金名稱, 本年度預算數基金來源, 本年度預算數基金用途, ...
    """
    if raw_path is None or not Path(raw_path).exists():
        logger.warning("fund_affairs: no raw data found")
        return None

    df = pd.read_csv(raw_path, encoding="utf-8")
    df.columns = df.columns.str.strip()

    rows = []
    for _, row in df.iterrows():
        fund_name = str(row.iloc[0]).strip()
        if not fund_name:
            continue
        source = pd.to_numeric(row.get('本年度預算數基金來源', 0), errors='coerce')
        usage = pd.to_numeric(row.get('本年度預算數基金用途', 0), errors='coerce')
        surplus = pd.to_numeric(row.get('本年度預算數賸餘', 0), errors='coerce')
        prev_source = pd.to_numeric(row.get('上年度預算數基金來源', 0), errors='coerce')
        prev_usage = pd.to_numeric(row.get('上年度預算數基金用途', 0), errors='coerce')

        if not pd.isna(source):
            rows.append({'fund_type': '政事型基金', 'fund_name': fund_name, 'item': '基金來源', 'amount': int(source), 'category': 'current'})
        if not pd.isna(usage):
            rows.append({'fund_type': '政事型基金', 'fund_name': fund_name, 'item': '基金用途', 'amount': int(usage), 'category': 'current'})
        if not pd.isna(surplus):
            rows.append({'fund_type': '政事型基金', 'fund_name': fund_name, 'item': '賸餘', 'amount': int(surplus), 'category': 'current'})
        if not pd.isna(prev_source):
            rows.append({'fund_type': '政事型基金', 'fund_name': fund_name, 'item': '基金來源', 'amount': int(prev_source), 'category': 'previous'})
        if not pd.isna(prev_usage):
            rows.append({'fund_type': '政事型基金', 'fund_name': fund_name, 'item': '基金用途', 'amount': int(prev_usage), 'category': 'previous'})

    result = pd.DataFrame(rows)
    if not result.empty:
        result['amount'] = pd.to_numeric(result['amount'], errors='coerce').fillna(0).astype('int64')
    return result


def run_fund_normalization(raw_paths: dict | None = None) -> dict[str, Path | None]:
    """Run all fund normalizers."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    results = {}

    maps = {
        'fund_operating': (normalize_fund_operating, 'fund_operating'),
        'fund_business': (normalize_fund_business, 'fund_business'),
        'fund_affairs': (normalize_fund_affairs, 'fund_affairs'),
    }

    for table_name, (fn, raw_name) in maps.items():
        raw_path = raw_paths.get(raw_name) if raw_paths else RAW_DIR / f"{raw_name}.csv"
        if isinstance(raw_path, str):
            raw_path = Path(raw_path)
        if raw_path and not raw_path.exists():
            raw_path = None

        df = fn(raw_path)
        if df is not None and not df.empty:
            out = PROCESSED_DIR / f"{table_name}.csv"
            df.to_csv(out, index=False, encoding="utf-8")
            results[table_name] = out
        else:
            results[table_name] = None

    return results
