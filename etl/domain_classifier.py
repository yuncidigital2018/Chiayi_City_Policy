"""Policy domain classifier — maps function_category & agency to policy_domain.

Modules:
- classify_expenditure(): function_category → policy_domain (from policy_domain_map.csv)
- classify_agency(): agency_name → policy_domain (from agency_policy_map.csv)
- generate_policy_domain_summary(): aggregate by domain with confidence stats
"""
import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DOMAIN_MAP_FILE = CONFIG_DIR / "policy_domain_map.csv"
AGENCY_MAP_FILE = CONFIG_DIR / "agency_policy_map.csv"


# ========================
# Map loaders
# ========================

def load_domain_map(map_path: Path | str | None = None) -> dict[str, dict]:
    """Load policy_domain_map.csv into a lookup dict.

    Returns:
        {function_category: {policy_domain, policy_domain_en, domain_order, confidence}}
    """
    map_path = Path(map_path) if map_path else DOMAIN_MAP_FILE
    if not map_path.exists():
        logger.error(f"Domain map not found: {map_path}")
        return {}

    df = pd.read_csv(map_path, encoding="utf-8")
    df.columns = df.columns.str.strip()

    required = {"function_category", "policy_domain", "policy_domain_en", "domain_order"}
    missing = required - set(df.columns)
    if missing:
        logger.error(f"Domain map missing columns: {missing}")
        return {}

    has_confidence = "confidence" in df.columns

    lookup = {}
    for _, row in df.iterrows():
        cat = str(row["function_category"]).strip()
        lookup[cat] = {
            "policy_domain": str(row["policy_domain"]).strip(),
            "policy_domain_en": str(row["policy_domain_en"]).strip(),
            "domain_order": int(row["domain_order"]),
            "confidence": str(row["confidence"]).strip() if has_confidence else "high",
        }
    return lookup


def load_agency_map(map_path: Path | str | None = None) -> dict[str, dict]:
    """Load agency_policy_map.csv into a lookup dict.

    Returns:
        {agency_name: {policy_domain, policy_domain_en, confidence, reason}}
    """
    map_path = Path(map_path) if map_path else AGENCY_MAP_FILE
    if not map_path.exists():
        logger.warning(f"Agency map not found: {map_path}")
        return {}

    df = pd.read_csv(map_path, encoding="utf-8")
    df.columns = df.columns.str.strip()

    required = {"agency_name", "policy_domain", "policy_domain_en", "confidence"}
    missing = required - set(df.columns)
    if missing:
        logger.error(f"Agency map missing columns: {missing}")
        return {}

    has_reason = "reason" in df.columns

    lookup = {}
    for _, row in df.iterrows():
        name = str(row["agency_name"]).strip()
        lookup[name] = {
            "policy_domain": str(row["policy_domain"]).strip(),
            "policy_domain_en": str(row["policy_domain_en"]).strip(),
            "confidence": str(row["confidence"]).strip(),
            "reason": str(row["reason"]).strip() if has_reason else "",
        }
    return lookup


# ========================
# Classifiers
# ========================

def classify_expenditure(
    input_path: Path | str | None = None,
    map_path: Path | str | None = None,
) -> pd.DataFrame | None:
    """Classify budget_expenditure_by_function with policy domains.

    Adds columns: policy_domain, policy_domain_en, domain_order, confidence
    """
    input_path = Path(input_path) if input_path else PROCESSED_DIR / "budget_expenditure_by_function.csv"
    if not input_path.exists():
        logger.error(f"Input not found: {input_path}")
        return None

    df = pd.read_csv(input_path, encoding="utf-8")
    df.columns = df.columns.str.strip()

    domain_map = load_domain_map(map_path)
    if not domain_map:
        return None

    # Validate unmapped
    unmapped = [c for c in df["function_category"].unique() if str(c).strip() not in domain_map]
    if unmapped:
        logger.warning(f"Unmapped function_categories: {unmapped}")
        logger.warning("Add these to config/policy_domain_map.csv")

    # Apply mapping
    for col, key in [
        ("policy_domain", "policy_domain"),
        ("policy_domain_en", "policy_domain_en"),
        ("domain_order", "domain_order"),
        ("confidence", "confidence"),
    ]:
        df[col] = df["function_category"].map(
            lambda x, k=key: domain_map.get(str(x).strip(), {}).get(k, "未分類" if k in ("policy_domain", "confidence") else 99 if k == "domain_order" else "Unclassified")
        )

    return df


def classify_agency(
    input_path: Path | str | None = None,
    map_path: Path | str | None = None,
) -> pd.DataFrame | None:
    """Classify budget_expenditure_by_agency with policy domains.

    Adds columns: policy_domain, policy_domain_en, agency_confidence, reason
    """
    input_path = Path(input_path) if input_path else PROCESSED_DIR / "budget_expenditure_by_agency.csv"
    if not input_path.exists():
        logger.error(f"Input not found: {input_path}")
        return None

    df = pd.read_csv(input_path, encoding="utf-8")
    df.columns = df.columns.str.strip()

    agency_map = load_agency_map(map_path)
    if not agency_map:
        logger.warning("No agency map found — agencies will be unclassified")
        df["policy_domain"] = "未分類"
        df["policy_domain_en"] = "Unclassified"
        df["agency_confidence"] = "none"
        df["reason"] = "no agency map"
        return df

    # Validate unmapped
    unmapped = [a for a in df["agency_name"].unique() if str(a).strip() not in agency_map]
    if unmapped:
        logger.warning(f"Unmapped agencies ({len(unmapped)}): {unmapped}")
        logger.warning("Add these to config/agency_policy_map.csv")

    for col, key in [
        ("policy_domain", "policy_domain"),
        ("policy_domain_en", "policy_domain_en"),
        ("agency_confidence", "confidence"),
        ("reason", "reason"),
    ]:
        default = "未分類" if key in ("policy_domain",) else "Unclassified" if key == "policy_domain_en" else "none" if key == "confidence" else "unmapped"
        df[col] = df["agency_name"].map(
            lambda x, k=key, d=default: agency_map.get(str(x).strip(), {}).get(k, d)
        )

    return df


# ========================
# Summary generators
# ========================

def generate_policy_domain_summary(classified_df: pd.DataFrame | None) -> pd.DataFrame | None:
    """Aggregate budget by policy_domain using L2 data.

    L2 items that map to a different domain than their L1 parent get their own line.
    L1 items without L2 breakdown are included as-is.
    Includes confidence breakdown per domain.
    """
    if classified_df is None or classified_df.empty:
        logger.warning("No classified data to summarize")
        return None

    rows = []
    l2_parents = set(
        classified_df.loc[classified_df["level"] == 2, "parent_code"].astype(str).str.strip()
    )
    for _, r in classified_df.iterrows():
        parent = str(r.get("parent_code", "")).strip()
        level = int(r["level"])
        if level == 2:
            rows.append(r)
        elif level == 1 and parent not in l2_parents:
            rows.append(r)

    detail = pd.DataFrame(rows)
    if detail.empty:
        return None

    summary = (
        detail.groupby(["policy_domain", "policy_domain_en", "domain_order"])
        .agg(
            recurring=("recurring", "sum"),
            capital=("capital", "sum"),
            amount=("amount", "sum"),
            high_confidence=("confidence", lambda x: (x == "high").sum()),
            medium_confidence=("confidence", lambda x: (x == "medium").sum()),
            low_confidence=("confidence", lambda x: (x == "low").sum()),
            item_count=("function_category", "count"),
        )
        .reset_index()
        .sort_values("domain_order")
    )

    total = summary["amount"].sum()
    summary["percentage"] = (summary["amount"] / total * 100).round(1) if total > 0 else 0.0

    # Overall confidence for the domain
    def domain_confidence(row):
        if row["low_confidence"] > 0:
            return "low"
        if row["medium_confidence"] > 0:
            return "medium"
        return "high"

    summary["confidence"] = summary.apply(domain_confidence, axis=1)

    return summary


def generate_agency_summary(agency_df: pd.DataFrame | None) -> pd.DataFrame | None:
    """Aggregate budget by policy_domain from agency perspective."""
    if agency_df is None or agency_df.empty:
        logger.warning("No agency data to summarize")
        return None

    summary = (
        agency_df.groupby(["policy_domain", "policy_domain_en"])
        .agg(
            amount=("amount", "sum"),
            agency_count=("agency_name", "count"),
            high=("agency_confidence", lambda x: (x == "high").sum()),
            medium=("agency_confidence", lambda x: (x == "medium").sum()),
            low=("agency_confidence", lambda x: (x == "low").sum()),
            none=("agency_confidence", lambda x: (x == "none").sum()),
        )
        .reset_index()
        .sort_values("amount", ascending=False)
    )

    total = summary["amount"].sum()
    summary["percentage"] = (summary["amount"] / total * 100).round(1) if total > 0 else 0.0

    return summary


# ========================
# Pipeline
# ========================

def run_classify_pipeline(
    input_path: Path | str | None = None,
    map_path: Path | str | None = None,
) -> dict:
    """Full classify pipeline: function + agency classify → summaries → save CSVs.

    Returns:
        {
            "classified_path": Path or None,
            "summary_path": Path or None,
            "agency_classified_path": Path or None,
            "agency_summary_path": Path or None,
            "unmapped_functions": int,
            "unmapped_agencies": int,
            "domain_count": int,
        }
    """
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    result = {
        "classified_path": None,
        "summary_path": None,
        "agency_classified_path": None,
        "agency_summary_path": None,
        "unmapped_functions": 0,
        "unmapped_agencies": 0,
        "domain_count": 0,
    }

    # 1. Classify by function (政事別)
    classified = classify_expenditure(input_path, map_path)
    if classified is not None:
        result["unmapped_functions"] = (classified["policy_domain"] == "未分類").sum()

        classified_path = PROCESSED_DIR / "budget_expenditure_classified.csv"
        classified.to_csv(classified_path, index=False, encoding="utf-8")
        logger.info(f"Saved classified → {classified_path} ({len(classified)} rows)")
        result["classified_path"] = classified_path

        summary = generate_policy_domain_summary(classified)
        if summary is not None and not summary.empty:
            summary_path = PROCESSED_DIR / "budget_by_policy_domain.csv"
            summary.to_csv(summary_path, index=False, encoding="utf-8")
            logger.info(f"Saved summary → {summary_path} ({len(summary)} domains)")
            result["summary_path"] = summary_path
            result["domain_count"] = len(summary)

    # 2. Classify by agency (機關別)
    agency_classified = classify_agency()
    if agency_classified is not None:
        result["unmapped_agencies"] = (agency_classified["policy_domain"] == "未分類").sum()

        agency_path = PROCESSED_DIR / "budget_agency_classified.csv"
        agency_classified.to_csv(agency_path, index=False, encoding="utf-8")
        logger.info(f"Saved agency classified → {agency_path} ({len(agency_classified)} rows)")
        result["agency_classified_path"] = agency_path

        agency_summary = generate_agency_summary(agency_classified)
        if agency_summary is not None and not agency_summary.empty:
            agency_summary_path = PROCESSED_DIR / "budget_agency_by_domain.csv"
            agency_summary.to_csv(agency_summary_path, index=False, encoding="utf-8")
            logger.info(f"Saved agency summary → {agency_summary_path}")
            result["agency_summary_path"] = agency_summary_path

    return result
