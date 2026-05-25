"""Shared test fixtures for ETL tests."""
import pytest
import pandas as pd
from pathlib import Path


@pytest.fixture
def tmp_csv(tmp_path):
    """Factory: write a DataFrame to a temp CSV and return the path."""
    def _write(df: pd.DataFrame, name: str = "test.csv") -> Path:
        p = tmp_path / name
        df.to_csv(p, index=False, encoding="utf-8")
        return p
    return _write


@pytest.fixture
def sample_population_annual_csv(tmp_csv):
    """Sample household scraper output for population_annual."""
    df = pd.DataFrame([
        {"年度": 113, "total": 262000, "male": 127000, "female": 135000, "households": 100000, "growth_pct": "-0.5%"},
        {"年度": 114, "total": 261500, "male": 126800, "female": 134700, "households": 100200, "growth_pct": "-0.2%"},
    ])
    return tmp_csv(df, "population_historical.csv")


@pytest.fixture
def sample_age_gender_csv(tmp_csv):
    """Sample age/gender pyramid data."""
    rows = []
    for age_range, male, female in [("0~4歲", 3000, 2800), ("5~9歲", 3500, 3200), ("10~14歲", 4000, 3800),
                                      ("15~19歲", 4500, 4200), ("20~24歲", 5000, 4800), ("25~29歲", 5500, 5200),
                                      ("30~34歲", 5000, 4800), ("35~39歲", 4500, 4300), ("40~44歲", 4000, 3900),
                                      ("45~49歲", 4200, 4100), ("50~54歲", 4500, 4400), ("55~59歲", 4800, 4700),
                                      ("60~64歲", 4000, 4100), ("65~69歲", 3500, 3800), ("70~74歲", 3000, 3500),
                                      ("75~79歲", 2000, 2800), ("80~84歲", 1200, 1800), ("85~89歲", 600, 1000),
                                      ("90~94歲", 200, 400), ("95歲以上", 50, 150)]:
        total = male + female
        rows.append({"age_group": age_range, "male": male, "female": female, "total": total})
    df = pd.DataFrame(rows)
    return tmp_csv(df, "population_age_gender.csv")


@pytest.fixture
def sample_village_csv(tmp_csv):
    """Sample village monthly data."""
    df = pd.DataFrame([
        {"年度": 115, "月份": 4, "行政區": "東區", "村里別": "東門里", "戶數": 1200, "male": 1500, "female": 1600, "人口數": 3100},
        {"年度": 115, "月份": 4, "行政區": "東區", "村里別": "竹圍里", "戶數": 800, "male": 1000, "female": 1100, "人口數": 2100},
        {"年度": 115, "月份": 4, "行政區": "西區", "村里別": "西門里", "戶數": 900, "male": 1100, "female": 1200, "人口數": 2300},
        {"年度": 115, "月份": 4, "行政區": "西區", "村里別": "番社里", "戶數": 700, "male": 850, "female": 950, "人口數": 1800},
    ] * 20)  # 80 rows to pass row_count_min
    return tmp_csv(df, "population_village_monthly.csv")


@pytest.fixture
def sample_revenue_csv(tmp_csv):
    """Sample budget revenue data (Open Chiayi format)."""
    df = pd.DataFrame([
        {"款": "1", "科目名稱": "稅課收入", "經常門（千元）": "5255680", "資本門（千元）": "-", "合計（千元）": "5255680"},
        {"款": "2", "科目名稱": "規費收入", "經常門（千元）": "180000", "資本門（千元）": "-", "合計（千元）": "180000"},
        {"款": "3", "科目名稱": "罰款及賠償收入", "經常門（千元）": "50000", "資本門（千元）": "-", "合計（千元）": "50000"},
        {"款": "4", "科目名稱": "財產收入", "經常門（千元）": "300000", "資本門（千元）": "10000", "合計（千元）": "310000"},
    ])
    return tmp_csv(df, "budget_revenue_115.csv")


@pytest.fixture
def sample_expenditure_function_csv(tmp_path):
    """Sample expenditure by function with L1/L2 hierarchy."""
    import csv
    p = tmp_path / "budget_expenditure_policy_115.csv"
    rows = [
        {"款": "1", "項": "", "名稱": "一般政務支出", "經常門": "800000", "資本門": "50000", "合計金額": "850000"},
        {"款": "", "項": "1", "名稱": "  行政管理", "經常門": "400000", "資本門": "20000", "合計金額": "420000"},
        {"款": "", "項": "2", "名稱": "  民意代表", "經常門": "400000", "資本門": "30000", "合計金額": "430000"},
        {"款": "2", "項": "", "名稱": "教育支出", "經常門": "2000000", "資本門": "200000", "合計金額": "2200000"},
        {"款": "", "項": "1", "名稱": "  學前教育", "經常門": "300000", "資本門": "50000", "合計金額": "350000"},
        {"款": "", "項": "2", "名稱": "  國民教育", "經常門": "1700000", "資本門": "150000", "合計金額": "1850000"},
    ]
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    return p


@pytest.fixture
def sample_expenditure_agency_csv(tmp_csv):
    """Sample expenditure by agency data."""
    df = pd.DataFrame([
        {"名稱": "教育處", "合計金額": "2200000"},
        {"名稱": "社會處", "合計金額": "1800000"},
        {"名稱": "財政處", "合計金額": "500000"},
    ])
    return tmp_csv(df, "budget_expenditure_dept_115.csv")
