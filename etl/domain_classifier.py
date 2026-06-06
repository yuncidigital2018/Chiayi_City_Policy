"""Policy domain classifier — maps function_category to policy_domain.

Reads budget_expenditure_by_function.csv, applies policy_domain_map.csv mapping,
and produces budget_by_policy_domain.csv with L1/L2 + domain classification.
"""
import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
MAP_FILE = CONFIG_DIR / "policy_domain_map.csv"


def load_domain_map(map_path: Path | str | None = None) -> dict[str, dict]:
    """Load policy_domain_map.csv into a lookup dict.

    Returns:
        {function_category: {policy_domain, policy_domain_en, domain_order}}
    """
    map_path = Path(map_path) if map_path else MAP_FILE
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

    lookup = {}
    for _, row in df.iterrows():
        cat = str(row["function_category"]).strip()
        lookup[cat] = {
            "policy_domain": str(row["policy_domain"]).strip(),
            "policy_domain_en": str(row["policy_domain_en"]).strip(),
            "domain_order": int(row["domain_order"]),
        }
    return lookup


def classify_expenditure(
    input_path: Path | str | None = None,
    map_path: Path | str | None = None,
) -> pd.DataFrame | None:
    """Classify budget_expenditure_by_function with policy domains.

    Args:
        input_path: Path to budget_expenditure_by_function.csv (default: processed dir)
        map_path: Path to policy_domain_map.csv (default: config dir)

    Returns:
        DataFrame with added policy_domain, policy_domain_en, domain_order columns.
        Returns None if input is missing or map has unmapped categories.
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

    # Validate: check for unmapped categories
    unmapped = []
    for cat in df["function_category"].unique():
        cat_clean = str(cat).strip()
        if cat_clean not in domain_map:
            unmapped.append(cat_clean)

    if unmapped:
        logger.warning(f"Unmapped function_categories: {unmapped}")
        logger.warning("Add these to config/policy_domain_map.csv")

    # Apply mapping
    df["policy_domain"] = df["function_category"].map(
        lambda x: domain_map.get(str(x).strip(), {}).get("policy_domain", "未分類")
    )
    df["policy_domain_en"] = df["function_category"].map(
        lambda x: domain_map.get(str(x).strip(), {}).get("policy_domain_en", "Unclassified")
    )
    df["domain_order"] = df["function_category"].map(
        lambda x: domain_map.get(str(x).strip(), {}).get("domain_order", 99)
    )

    return df


def generate_policy_domain_summary(classified_df: pd.DataFrame | None) -> pd.DataFrame | None:
    """Aggregate budget by policy_domain using L2 data.

    L2 items that map to a different domain than their L1 parent get their own line.
    L1 items without L2 breakdown are included as-is.
    """
    if classified_df is None or classified_df.empty:
        logger.warning("No classified data to summarize")
        return None

    # Use L2 rows for detailed domain mapping; fall back to L1 if no L2 exists
    l1_codes = set(classified_df.loc[classified_df["level"] == 1, "parent_code"].unique())

    rows = []
    for _, r in classified_df.iterrows():
        parent = str(r.get("parent_code", "")).strip()
        level = int(r["level"])
        # Include L2 rows (they have the accurate domain mapping)
        # Include L1 rows only if no L2 children exist for that parent
        if level == 2:
            rows.append(r)
        elif level == 1 and parent not in set(
            classified_df.loc[classified_df["level"] == 2, "parent_code"].astype(str).str.strip()
        ):
            rows.append(r)

    detail = pd.DataFrame(rows)
    if detail.empty:
        return None

    summary = (
        detail.groupby(["policy_domain", "policy_domain_en", "domain_order"])
        .agg(recurring=("recurring", "sum"), capital=("capital", "sum"), amount=("amount", "sum"))
        .reset_index()
        .sort_values("domain_order")
    )

    total = summary["amount"].sum()
    summary["percentage"] = (summary["amount"] / total * 100).round(1) if total > 0 else 0.0

    return summary


def run_classify_pipeline(
    input_path: Path | str | None = None,
    map_path: Path | str | None = None,
) -> dict:
    """Full classify pipeline: classify → summary → save CSVs.

    Returns:
        {
            "classified_path": Path or None,
            "summary_path": Path or None,
            "unmapped_count": int,
            "domain_count": int,
        }
    """
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # Classify
    classified = classify_expenditure(input_path, map_path)
    if classified is None:
        return {"classified_path": None, "summary_path": None, "unmapped_count": -1, "domain_count": 0}

    unmapped_count = (classified["policy_domain"] == "未分類").sum()

    # Save classified
    classified_path = PROCESSED_DIR / "budget_expenditure_classified.csv"
    classified.to_csv(classified_path, index=False, encoding="utf-8")
    logger.info(f"Saved classified → {classified_path} ({len(classified)} rows)")

    # Generate summary
    summary = generate_policy_domain_summary(classified)
    if summary is not None and not summary.empty:
        summary_path = PROCESSED_DIR / "budget_by_policy_domain.csv"
        summary.to_csv(summary_path, index=False, encoding="utf-8")
        logger.info(f"Saved summary → {summary_path} ({len(summary)} domains)")
    else:
        summary_path = None

    return {
        "classified_path": classified_path,
        "summary_path": summary_path,
        "unmapped_count": unmapped_count,
        "domain_count": len(summary) if summary is not None else 0,
    }
