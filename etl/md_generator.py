"""Markdown Generator — produce structured Markdown reports from processed data."""
from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

import pandas as pd
from jinja2 import Environment, BaseLoader

from etl.normalizer import PROCESSED_DIR

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = PROJECT_ROOT / "content"


# ========================
# Helpers (defined before env so filters work)
# ========================

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


def _fmt(n):
    """Format number with commas, handle None/NaN."""
    try:
        if n is None or (isinstance(n, float) and n != n):
            return '—'
        return f"{int(n):,}"
    except (ValueError, TypeError):
        return str(n)


# ========================
# Shared Jinja2 environment
# ========================

_env = Environment(loader=BaseLoader())
_env.filters["format_number"] = _format_number
_env.filters["format_change"] = _format_change


def _tpl(source: str):
    return _env.from_string(source)


# ========================
# Templates
# ========================

POPULATION_OVERVIEW_TEMPLATE = _tpl("""# 嘉義市人口總覽

> 資料更新日期：{{ generated_at }}

## 最新年度人口摘要

| 指標 | 數值 |
|------|------|
{% for row in summary_rows %}
| {{ row.metric }} | {{ row.value | default('—') }} |
{% endfor %}

## 年齡結構指標

| 指標 | 數值 |
|------|------|
{% for row in age_indicators %}
| {{ row.metric }} | {{ row.value }} |
{% endfor %}

## 歷年人口趨勢

| 年度 | 總人口 | 男性 | 女性 | 戶數 | 增減率 |
|------|--------|------|------|------|--------|
{% for row in annual_rows %}
| {{ row.year }} | {{ row.total_population }} | {{ row.male }} | {{ row.female }} | {{ row.households | default('—') }} | {{ row.growth_pct | default('—') }} |
{% endfor %}

## 人口金字塔（性別年齡分布）

| 年齡層 | 男性 | 女性 | 合計 |
|--------|------|------|------|
{% for row in pyramid_rows %}
| {{ row.age_group }} | {{ row.male | format_number }} | {{ row.female | format_number }} | {{ row.total | format_number }} |
{% endfor %}

## 重點觀察

{% if latest_population %}
- **最新人口數**：{{ latest_population | format_number }} 人
{% endif %}
{% if aging_index %}
- **老化指數**：{{ aging_index }}（65歲以上/0-14歲 × 100）
{% endif %}
{% if dependency_ratio %}
- **扶養比**：{{ dependency_ratio }}
{% endif %}
""")

BUDGET_REVENUE_TEMPLATE = _tpl("""# 歲入來源別預算結構

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

BUDGET_EXPENDITURE_TEMPLATE = _tpl("""# 歲出預算結構

> 資料更新日期：{{ generated_at }}

## {{ fiscal_year }} 年度歲出（政事別）

{% for item in expenditure_tree %}
{% if item.level == 1 %}
### {{ item.idx }}. {{ item.function_category }} — {{ item.amount_fmt }}（{{ item.percentage }}%）

| 子項目 | 經常門 | 資本門 | 合計（千元） |
|--------|--------|--------|-------------|{% for child in item.children %}
| {{ child.function_category }} | {{ child.recurring_fmt }} | {{ child.capital_fmt }} | {{ child.amount_fmt }} |{% endfor %}

{% endif %}
{% endfor %}
## 機關別預算 Top 10

| 機關 | 金額（千元） | 占比 |
|------|-------------|------|{% for row in agency_top %}
| {{ row.agency_name }} | {{ row.amount | default('—') }} | {{ row.percentage | default('—') }}% |{% endfor %}
""")

POPULATION_VILLAGE_TEMPLATE = _tpl("""# 區里人口分布

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


# ========================
# Generators
# ========================

def generate_population_overview(df: pd.DataFrame | None,
                                  df_age: pd.DataFrame | None = None) -> str | None:
    """Generate population overview Markdown with age pyramid."""
    if df is None or df.empty:
        return None

    generated_at = datetime.now().strftime("%Y-%m-%d")

    latest = df.iloc[-1] if len(df) > 0 else None
    summary_rows = []
    if latest is not None:
        summary_rows = [
            {"metric": "年度", "value": latest.get("year", "—")},
            {"metric": "總人口", "value": _format_number(latest.get("total_population", 0))},
            {"metric": "男性", "value": _format_number(latest.get("male", 0))},
            {"metric": "女性", "value": _format_number(latest.get("female", 0))},
            {"metric": "男女性別比",
             "value": f"{latest.get('male', 0) / max(latest.get('female', 1), 1) * 100:.1f}"},
            {"metric": "戶數", "value": _format_number(latest.get("households", 0))},
        ]

    annual_rows = df.to_dict("records")

    # Age pyramid rows and indicators
    pyramid_rows = []
    aging_index = None
    dependency_ratio = None
    age_indicators = []
    if df_age is not None and not df_age.empty:
        pyramid_rows = df_age.sort_values("age_midpoint").to_dict("records")

        young_mask = df_age["age_group"].isin(["0~4歲", "5~9歲", "10~14歲"])
        working_mask = df_age["age_group"].isin(["15~19歲", "20~24歲", "25~29歲", "30~34歲",
                                                  "35~39歲", "40~44歲", "45~49歲", "50~54歲",
                                                  "55~59歲", "60~64歲"])
        old_mask = df_age["age_group"].isin(["65~69歲", "70~74歲", "75~79歲", "80~84歲",
                                              "85~89歲", "90~94歲", "95~99歲", "100歲以上"])
        young_pop = int(df_age[young_mask]["total"].sum())
        working_pop = int(df_age[working_mask]["total"].sum())
        old_pop = int(df_age[old_mask]["total"].sum())

        if young_pop > 0:
            aging_index = f"{old_pop / young_pop * 100:.1f}"
        dependency_ratio = f"{(young_pop + old_pop) / working_pop * 100:.1f}" if working_pop > 0 else "—"

        age_indicators = [
            {"metric": "0-14歲（幼年人口）", "value": _format_number(young_pop)},
            {"metric": "15-64歲（工作年齡）", "value": _format_number(working_pop)},
            {"metric": "65歲以上（老年人口）", "value": _format_number(old_pop)},
        ]

    return POPULATION_OVERVIEW_TEMPLATE.render(
        generated_at=generated_at,
        summary_rows=summary_rows,
        annual_rows=annual_rows,
        latest_population=latest.get("total_population") if latest is not None else None,
        pyramid_rows=pyramid_rows,
        aging_index=aging_index,
        dependency_ratio=dependency_ratio,
        age_indicators=age_indicators,
    )


def generate_budget_revenue(df: pd.DataFrame | None) -> str | None:
    """Generate budget revenue Markdown."""
    if df is None or df.empty:
        return None

    generated_at = datetime.now().strftime("%Y-%m-%d")
    revenue_rows = df.to_dict("records")

    total = df["amount"].sum()
    for row in revenue_rows:
        row["percentage"] = f"{row['amount'] / total * 100:.1f}" if total > 0 else "—"

    return BUDGET_REVENUE_TEMPLATE.render(
        generated_at=generated_at,
        fiscal_year=df["fiscal_year"].iloc[-1] if "fiscal_year" in df.columns else "—",
        revenue_rows=revenue_rows,
        yearly_rows=[],
    )


def generate_budget_expenditure(df_func: pd.DataFrame | None, df_agency: pd.DataFrame | None) -> str | None:
    """Generate budget expenditure Markdown with hierarchical structure."""
    if df_func is None or df_func.empty:
        return None

    generated_at = datetime.now().strftime("%Y-%m-%d")

    tree = []
    children_map = {}
    l1_items = []

    for _, row in df_func.iterrows():
        level = int(row.get('level', 1))
        parent = str(row.get('parent_code', '')).strip()
        if level == 1:
            l1_items.append(row)
            children_map[parent] = []
        elif level == 2 and parent:
            if parent not in children_map:
                children_map[parent] = []
            children_map[parent].append(row)

    total = df_func[df_func['level'] == 1]['amount'].sum()

    expenditure_tree = []
    for idx, item in enumerate(l1_items, 1):
        parent = str(item.get('parent_code', '')).strip()
        pct = f"{item['amount'] / total * 100:.1f}" if total > 0 else '0.0'
        children = []
        for child in children_map.get(parent, []):
            children.append({
                'function_category': child['function_category'],
                'recurring_fmt': _fmt(child.get('recurring')),
                'capital_fmt': _fmt(child.get('capital')),
                'amount_fmt': _fmt(child.get('amount')),
            })
        expenditure_tree.append({
            'idx': idx,
            'level': 1,
            'function_category': item['function_category'],
            'recurring_fmt': _fmt(item.get('recurring')),
            'capital_fmt': _fmt(item.get('capital')),
            'amount_fmt': _fmt(item.get('amount')),
            'percentage': pct,
            'children': children,
        })

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
        expenditure_tree=expenditure_tree,
        agency_top=agency_top,
    )


def generate_population_village(df: pd.DataFrame | None) -> str | None:
    """Generate village-level population distribution Markdown."""
    if df is None or df.empty:
        return None

    generated_at = datetime.now().strftime("%Y-%m-%d")
    year = int(df["year"].max()) if "year" in df.columns else "—"
    month = int(df["month"].max()) if "month" in df.columns else "—"

    east = df[df.get("district", "") == "東區"].nlargest(20, "population") if "population" in df.columns else pd.DataFrame()
    west = df[df.get("district", "") == "西區"].nlargest(20, "population") if "population" in df.columns else pd.DataFrame()

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
    """Generate all Markdown files from processed data."""
    results = {}

    (CONTENT_DIR / "population").mkdir(parents=True, exist_ok=True)
    (CONTENT_DIR / "budget").mkdir(parents=True, exist_ok=True)

    # Population overview (with age-gender pyramid)
    pop_path = processed_paths.get("population_annual") if processed_paths else None
    pop_path = pop_path or (PROCESSED_DIR / "population_annual.csv")
    df_pop = pd.read_csv(pop_path, encoding="utf-8") if pop_path and Path(pop_path).exists() else None

    age_path = processed_paths.get("population_age_gender") if processed_paths else None
    age_path = age_path or (PROCESSED_DIR / "population_age_gender.csv")
    df_age = pd.read_csv(age_path, encoding="utf-8") if age_path and Path(age_path).exists() else None

    md = generate_population_overview(df_pop, df_age)
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
