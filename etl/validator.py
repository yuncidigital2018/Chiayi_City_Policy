"""Data Validator — validate processed CSVs against expected schemas.

Run after normalization to catch data quality issues early.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"


@dataclass
class ValidationResult:
    table: str
    passed: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    row_count: int = 0

    def __str__(self):
        status = "✅" if self.passed else "❌"
        lines = [f"{status} {self.table} ({self.row_count} rows)"]
        for e in self.errors:
            lines.append(f"  ERROR: {e}")
        for w in self.warnings:
            lines.append(f"  WARN:  {w}")
        return "\n".join(lines)


# ── Schema definitions ──────────────────────────────────────────────

SCHEMAS: dict[str, dict[str, Any]] = {
    "population_annual": {
        "required_cols": ["year", "total_population", "male", "female"],
        "optional_cols": ["natural_increase", "social_increase", "households", "growth_pct"],
        "int_cols": ["year", "total_population", "male", "female", "natural_increase", "social_increase", "households"],
        "range_checks": {
            "total_population": (100000, 500000),  # Chiayi ~260k
            "male": (50000, 250000),
            "female": (50000, 250000),
        },
    },
    "population_age_gender": {
        "required_cols": ["age_group", "male", "female", "total"],
        "optional_cols": ["age_midpoint"],
        "int_cols": ["male", "female", "total"],
        "row_count_min": 15,  # At least 15 age groups
    },
    "population_village_monthly": {
        "required_cols": ["year", "month", "district", "village", "population"],
        "optional_cols": ["households", "male", "female"],
        "int_cols": ["year", "month", "population", "households"],
        "row_count_min": 40,  # Chiayi has ~84 villages
    },
    "budget_revenue_by_source": {
        "required_cols": ["fiscal_year", "source_category", "amount"],
        "optional_cols": [],
        "int_cols": ["fiscal_year"],
        "row_count_min": 3,  # At least a few revenue categories
    },
    "budget_expenditure_by_function": {
        "required_cols": ["fiscal_year", "level", "function_category", "amount"],
        "optional_cols": ["parent_code", "code", "recurring", "capital"],
        "int_cols": ["fiscal_year", "level"],
        "row_count_min": 5,
    },
    "budget_expenditure_by_agency": {
        "required_cols": ["fiscal_year", "agency_name", "amount"],
        "optional_cols": [],
        "int_cols": ["fiscal_year"],
        "row_count_min": 3,
    },
    "fund_operating": {
        "required_cols": ["item", "amount"],
        "optional_cols": [],
        "row_count_min": 1,
    },
    "fund_business": {
        "required_cols": ["item", "amount"],
        "optional_cols": [],
        "row_count_min": 1,
    },
    "fund_affairs": {
        "required_cols": ["item", "amount"],
        "optional_cols": [],
        "row_count_min": 1,
    },
}


def validate_table(table_name: str, df: pd.DataFrame) -> ValidationResult:
    """Validate a single processed DataFrame against its schema."""
    schema = SCHEMAS.get(table_name)
    if schema is None:
        return ValidationResult(table=table_name, passed=True, warnings=["No schema defined — skipped"])

    errors: list[str] = []
    warnings: list[str] = []
    result = ValidationResult(table=table_name, passed=False, row_count=len(df))

    # 1. Empty check
    if df.empty:
        errors.append("DataFrame is empty")
        result.errors = errors
        return result

    # 2. Required columns
    missing = [c for c in schema["required_cols"] if c not in df.columns]
    if missing:
        errors.append(f"Missing required columns: {missing}")

    # 3. Null check on required columns
    for col in schema["required_cols"]:
        if col in df.columns:
            null_count = df[col].isna().sum()
            if null_count > 0:
                pct = null_count / len(df) * 100
                if pct > 50:
                    errors.append(f"Column '{col}' has {pct:.0f}% nulls")
                elif pct > 5:
                    warnings.append(f"Column '{col}' has {null_count} nulls ({pct:.1f}%)")

    # 4. Type checks
    for col in schema.get("int_cols", []):
        if col in df.columns:
            non_numeric = pd.to_numeric(df[col], errors="coerce").isna().sum() - df[col].isna().sum()
            if non_numeric > 0:
                errors.append(f"Column '{col}' has {non_numeric} non-numeric values")

    # 5. Range checks
    for col, (lo, hi) in schema.get("range_checks", {}).items():
        if col in df.columns:
            numeric = pd.to_numeric(df[col], errors="coerce")
            outliers = ((numeric < lo) | (numeric > hi)).sum()
            if outliers > 0:
                warnings.append(f"Column '{col}' has {outliers} values outside [{lo:,}, {hi:,}]")

    # 6. Row count
    if "row_count_min" in schema and len(df) < schema["row_count_min"]:
        warnings.append(f"Only {len(df)} rows (expected >= {schema['row_count_min']})")

    # 7. Duplicate check
    if len(df) > 1:
        dup_count = df.duplicated().sum()
        if dup_count > 0:
            warnings.append(f"{dup_count} duplicate rows detected")

    result.errors = errors
    result.warnings = warnings
    result.passed = len(errors) == 0
    return result


def validate_all(processed_dir: Path | None = None) -> list[ValidationResult]:
    """Validate all processed CSVs."""
    processed_dir = processed_dir or PROCESSED_DIR
    results = []

    for csv_file in sorted(processed_dir.glob("*.csv")):
        table_name = csv_file.stem
        try:
            df = pd.read_csv(csv_file, encoding="utf-8")
            vr = validate_table(table_name, df)
        except Exception as e:
            vr = ValidationResult(table=table_name, passed=False, errors=[f"Failed to read: {e}"])

        results.append(vr)
        logger.info(str(vr))

    # Summary
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed
    logger.info(f"Validation summary: {passed}/{total} passed, {failed} failed")

    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    results = validate_all()
    exit(0 if all(r.passed for r in results) else 1)
