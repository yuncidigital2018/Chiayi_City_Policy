"""Markdown Generator — produce structured Markdown reports from processed data."""
import logging
from datetime import datetime
from pathlib import Path

import pandas as pd
from jinja2 import Template

from etl.normalizer import PROCESSED_DIR

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = PROJECT_ROOT / "content"

# ========================
# Templates
# ========================

POPULATION_OVERVIEW_TEMPLATE = Template("""# 嘉義市人口總覽

> 資料更新日期：{{ generated_at }}

## 最新年度人口摘要

| 指標 | 數值 |
|------|------|
{% for row in summary_rows %}
| {{ row.metric }} | {{ row.value | default('—') }} |
{% endfor %}

## 歷年人口趨勢

| 年度 | 總人口 | 男性 | 女性 | 自然增減 | 社會增減 |
|------|--------|------|------|----------|----------|
{% for row in annual_rows %}
| {{ row.year }} | {{ row.total_population }} | {{ row.male }} | {{ row.female }} | {{ row.natural_increase }} | {{ row.social_increase }} |
{% endfor %}

## 重點觀察

{% if latest_population %}
- **最新人口數**：{{ latest_population | format_number }} 人
{% endif %}
{% if latest_change %}
- **年度增減**：{{ latest_change | format_change }} 人
{% endif %}
""")

BUDGET_REVENUE_TEMPLATE = Template("""# 歲入來源別預算結構

> 資料更新日期：{{ generated_at }}

## {{ fiscal_year }} 年度歲入總覽

| 來源類別 | 金額（千元） | 占比 |
|----------|-------------|------|
{% for row in revenue_rows %}
| {{ row.source_category }} | {{ row.amount | default('—') }} | {{ row.percentage | default('—') }}% |
{% endfor %}

## 歷年趨勢

| 年度 | 總歲入 | 地方稅 | 統籌分配 | 補助款 |
|------|--------|--------|----------|--------|
{% for row in yearly_rows %}
| {{ row.fiscal_year }} | {{ row.total }} | {{ row.tax }} | {{ row.share }} | {{ row.grant }} |
{% endfor %}
""")

BUDGET_EXPENDITURE_TEMPLATE = Template("""# 歲出預算結構

> 資料更新日期：{{ generated_at }}

## {{ fiscal_year }} 年度歲出（政事別）

| 政事別 | 金額（千元） | 占比 |
|--------|-------------|------|
{% for row in expenditure_rows %}
| {{ row.function_category }} | {{ row.amount | default('—') }} | {{ row.percentage | default('—') }}% |
{% endfor %}

## 機關別預算 Top 10

| 機關 | 金額（千元） | 占比 |
|------|-------------|------|
{% for row in agency_top %}
| {{ row.agency_name }} | {{ row.amount | default('—') }} | {{ row.percentage | default('—') }}% |
{% endfor %}
""")

POPULATION_VILLAGE_TEMPLATE = Template("""# 區里人口分布

> 資料更新日期：{{ generated_at }}
> 期間：{{ year }}年{{ month }}月

## 東區各里人口 Top 20

| 里名 | 戶數 | 人口數 |
|------|------|--------|
{% for row in east_top %}
| {{ row.village }} | {{ row.households }} | {{ row.population }} |
{% endfor %}

## 西區各里人口 Top 20

| 里名 | 戶數 | 人口數 |
|------|------|--------|
{% for row in west_top %}
| {{ row.village }} | {{ row.households }} | {{ row.population }} |
{% endfor %}

## 東西區人口比較

| 區域 | 總人口 | 總戶數 | 平均每里人口 |
|------|--------|--------|-------------|
{% for row in district_summary %}
| {{ row.district }} | {{ row.total_population }} | {{ row.total_households }} | {{ row.avg_per_village }} |
{% endfor %}
""")


def _format_number(n) -> str:
    """Format number with commas."""
    try:
        return f"{int(n):,}"
    except (ValueError, TypeError):
        return str(n)


def _format_change(n) -> str:
    """Format change with +/- sign."""
    try:
        n = int(n)
        return f"+{n:,}" if n > 0 else f"{n:,}"
    except (ValueError, TypeError):
        return str(n)


# Register filters
for tpl in [POPULATION_OVERVIEW_TEMPLATE, BUDGET_REVENUE_TEMPLATE,
            BUDGET_EXPENDITURE_TEMPLATE, POPULATION_VILLAGE_TEMPLATE]:
    tpl.environment.filters["format_number"] = _format_number
    tpl.environment.filters["format_change"] = _format_change


def generate_population_overview(df: pd.DataFrame | None) -> str | None:
    """Generate population overview Markdown."""
    if df is None or df.empty:
        return None

    generated_at = datetime.now().strftime("%Y-%m-%d")

    # Summary rows
    latest = df.iloc[-1] if len(df) > 0 else None
    summary_rows = []
    if latest is not None:
        summary_rows = [
            {"metric": "年度", "value": latest.get("year", "—")},
            {"metric": "總人口", "value": _format_number(latest.get("total_population", 0))},
            {"metric": "男性", "value": _format_number(latest.get("male", 0))},
            {"metric": "女性", "value": _format_number(latest.get("female", 0))},
            {"metric": "男女性別比", "value": f"{latest.get('male', 0) / max(latest.get('female', 1), 1) * 100:.1f}" if latest.get("female") else "—"},
            {"metric": "自然增減", "value": _format_change(latest.get("natural_increase", 0))},
            {"metric": "社會增減", "value": _format_change(latest.get("social_increase", 0))},
        ]

    annual_rows = df.to_dict("records")

    return POPULATION_OVERVIEW_TEMPLATE.render(
        generated_at=generated_at,
        summary_rows=summary_rows,
        annual_rows=annual_rows,
        latest_population=latest.get("total_population") if latest is not None else None,
        latest_change=latest.get("natural_increase", 0) + latest.get("social_increase", 0) if latest is not None else None,
    )


def generate_budget_revenue(df: pd.DataFrame | None) -> str | None:
    """Generate budget revenue Markdown."""
    if df is None or df.empty:
        return None

    generated_at = datetime.now().strftime("%Y-%m-%d")
    revenue_rows = df.to_dict("records")

    # Calculate percentages
    total = df["amount"].sum()
    for row in revenue_rows:
        row["percentage"] = f"{row['amount'] / total * 100:.1f}" if total > 0 else "—"

    return BUDGET_REVENUE_TEMPLATE.render(
        generated_at=generated_at,
        fiscal_year=df["fiscal_year"].iloc[-1] if "fiscal_year" in df.columns else "—",
        revenue_rows=revenue_rows,
        yearly_rows=[],  # Placeholder for multi-year comparison
    )


def generate_budget_expenditure(df_func: pd.DataFrame | None, df_agency: pd.DataFrame | None) -> str | None:
    """Generate budget expenditure Markdown."""
    if df_func is None or df_func.empty:
        return None

    generated_at = datetime.now().strftime("%Y-%m-%d")
    expenditure_rows = df_func.to_dict("records")

    # Calculate percentages
    total = df_func["amount"].sum()
    for row in expenditure_rows:
        row["percentage"] = f"{row['amount'] / total * 100:.1f}" if total > 0 else "—"

    # Agency top 10
    agency_top = []
    if df_agency is not None and not df_agency.empty:
        agency_sorted = df_agency.nlargest(10, "amount")
        agency_total = df_agency["amount"].sum()
        agency_top = agency_sorted.to_dict("records")
        for row in agency_top:
            row["percentage"] = f"{row['amount'] / agency_total * 100:.1f}" if agency_total > 0 else "—"

    return BUDGET_EXPENDITURE_TEMPLATE.render(
        generated_at=generated_at,
        fiscal_year=df_func["fiscal_year"].iloc[-1] if "fiscal_year" in df_func.columns else "—",
        expenditure_rows=expenditure_rows,
        agency_top=agency_top,
    )


def generate_population_village(df: pd.DataFrame | None) -> str | None:
    """Generate village-level population distribution Markdown."""
    if df is None or df.empty:
        return None

    generated_at = datetime.now().strftime("%Y-%m-%d")
    year = int(df["year"].max()) if "year" in df.columns else "—"
    month = int(df["month"].max()) if "month" in df.columns else "—"

    # Split by district
    east = df[df.get("district", "") == "東區"].nlargest(20, "population") if "population" in df.columns else pd.DataFrame()
    west = df[df.get("district", "") == "西區"].nlargest(20, "population") if "population" in df.columns else pd.DataFrame()

    # District summary
    district_summary = []
    if "district" in df.columns:
        for d in df["district"].unique():
            subset = df[df["district"] == d]
            district_summary.append({
                "district": d,
                "total_population": subset["population"].sum() if "population" in subset.columns else 0,
                "total_households": subset["households"].sum() if "households" in subset.columns else 0,
                "avg_per_village": round(subset["population"].mean()) if "population" in subset.columns and len(subset) > 0 else 0,
            })

    return POPULATION_VILLAGE_TEMPLATE.render(
        generated_at=generated_at,
        year=year,
        month=month,
        east_top=east.to_dict("records"),
        west_top=west.to_dict("records"),
        district_summary=district_summary,
    )


def run_markdown_generation(processed_paths: dict[str, Path] | None = None) -> dict[str, Path]:
    """Generate all Markdown files from processed data.

    Args:
        processed_paths: Dict mapping table_name → processed CSV path

    Returns:
        Dict mapping content_key → generated Markdown path
    """
    results = {}

    # Ensure output directories exist
    (CONTENT_DIR / "population").mkdir(parents=True, exist_ok=True)
    (CONTENT_DIR / "budget").mkdir(parents=True, exist_ok=True)

    # Population overview
    pop_path = processed_paths.get("population_annual") if processed_paths else None
    pop_path = pop_path or (PROCESSED_DIR / "population_annual.csv")
    df_pop = pd.read_csv(pop_path, encoding="utf-8") if pop_path and Path(pop_path).exists() else None
    md = generate_population_overview(df_pop)
    if md:
        out_path = CONTENT_DIR / "population" / "overview.md"
        out_path.write_text(md, encoding="utf-8")
        results["population_overview"] = out_path
        logger.info(f"Generated {out_path}")

    # Budget revenue
    rev_path = processed_paths.get("budget_revenue_by_source") if processed_paths else None
    rev_path = rev_path or (PROCESSED_DIR / "budget_revenue_by_source.csv")
    df_rev = pd.read_csv(rev_path, encoding="utf-8") if rev_path and Path(rev_path).exists() else None
    md = generate_budget_revenue(df_rev)
    if md:
        out_path = CONTENT_DIR / "budget" / "revenue_structure.md"
        out_path.write_text(md, encoding="utf-8")
        results["budget_revenue"] = out_path
        logger.info(f"Generated {out_path}")

    # Budget expenditure
    exp_func_path = processed_paths.get("budget_expenditure_by_function") if processed_paths else None
    exp_func_path = exp_func_path or (PROCESSED_DIR / "budget_expenditure_by_function.csv")
    df_func = pd.read_csv(exp_func_path, encoding="utf-8") if exp_func_path and Path(exp_func_path).exists() else None

    exp_agency_path = processed_paths.get("budget_expenditure_by_agency") if processed_paths else None
    exp_agency_path = exp_agency_path or (PROCESSED_DIR / "budget_expenditure_by_agency.csv")
    df_agency = pd.read_csv(exp_agency_path, encoding="utf-8") if exp_agency_path and Path(exp_agency_path).exists() else None

    md = generate_budget_expenditure(df_func, df_agency)
    if md:
        out_path = CONTENT_DIR / "budget" / "expenditure_structure.md"
        out_path.write_text(md, encoding="utf-8")
        results["budget_expenditure"] = out_path
        logger.info(f"Generated {out_path}")

    # Village population
    village_path = processed_paths.get("population_village_monthly") if processed_paths else None
    village_path = village_path or (PROCESSED_DIR / "population_village_monthly.csv")
    df_village = pd.read_csv(village_path, encoding="utf-8") if village_path and Path(village_path).exists() else None
    md = generate_population_village(df_village)
    if md:
        out_path = CONTENT_DIR / "population" / "districts.md"
        out_path.write_text(md, encoding="utf-8")
        results["population_districts"] = out_path
        logger.info(f"Generated {out_path}")

    return results
