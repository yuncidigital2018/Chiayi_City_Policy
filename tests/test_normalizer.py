"""Unit tests for etl/normalizer.py."""
import pandas as pd
import pytest

from etl.normalizer import (
    normalize_population_annual,
    normalize_population_age_gender,
    normalize_population_village,
    normalize_budget_revenue,
    normalize_budget_expenditure_function,
    normalize_budget_expenditure_agency,
    _parse_age_midpoint,
    _convert_schema,
)


# ── Helpers ──

class TestParseAgeMidpoint:
    def test_range(self):
        assert _parse_age_midpoint("0~4歲") == 2.0
        assert _parse_age_midpoint("25~29歲") == 27.0

    def test_single(self):
        assert _parse_age_midpoint("95歲以上") == 95.0

    def test_unknown(self):
        assert _parse_age_midpoint("unknown") == 0.0


class TestConvertSchema:
    def test_int_conversion(self):
        df = pd.DataFrame({"a": ["1", "2", "3"], "b": [1.1, 2.2, 3.3]})
        result = _convert_schema(df, {"a": "int64", "b": "float64"})
        assert result["a"].dtype == "int64"
        assert result["b"].dtype == "float64"

    def test_coerce_errors(self):
        df = pd.DataFrame({"a": ["1", "bad", "3"]})
        result = _convert_schema(df, {"a": "int64"})
        # "bad" becomes 0 (fillna(0))
        assert result["a"].iloc[1] == 0


# ── Population Normalizers ──

class TestNormalizePopulationAnnual:
    def test_basic(self, sample_population_annual_csv):
        df = normalize_population_annual(sample_population_annual_csv)
        assert df is not None
        assert len(df) == 2
        assert set(["year", "total_population", "male", "female"]).issubset(df.columns)
        assert df["year"].tolist() == [113, 114]
        assert df["total_population"].iloc[0] == 262000

    def test_none_path(self):
        assert normalize_population_annual(None) is None

    def test_missing_file(self, tmp_path):
        assert normalize_population_annual(tmp_path / "nope.csv") is None


class TestNormalizePopulationAgeGender:
    def test_basic(self, sample_age_gender_csv):
        df = normalize_population_age_gender(sample_age_gender_csv)
        assert df is not None
        assert len(df) == 20
        assert "age_midpoint" in df.columns
        assert df["age_midpoint"].iloc[0] == 2.0  # 0~4歲

    def test_none_path(self):
        assert normalize_population_age_gender(None) is None


class TestNormalizePopulationVillage:
    def test_basic(self, sample_village_csv):
        df = normalize_population_village(sample_village_csv)
        assert df is not None
        assert len(df) == 80
        assert "district" in df.columns
        assert df["district"].iloc[0] == "東區"

    def test_none_path(self):
        assert normalize_population_village(None) is None


# ── Budget Normalizers ──

class TestNormalizeBudgetRevenue:
    def test_basic(self, sample_revenue_csv):
        df = normalize_budget_revenue(sample_revenue_csv, fiscal_year=115)
        assert df is not None
        assert len(df) == 4
        assert "source_category" in df.columns
        assert "amount" in df.columns
        assert df["fiscal_year"].iloc[0] == 115
        assert df["amount"].iloc[0] == 5255680.0

    def test_none_path(self):
        assert normalize_budget_revenue(None) is None


class TestNormalizeBudgetExpenditureFunction:
    def test_hierarchy(self, sample_expenditure_function_csv):
        df = normalize_budget_expenditure_function(sample_expenditure_function_csv, fiscal_year=115)
        assert df is not None
        # 2 L1 + 4 L2 = 6 rows
        assert len(df) == 6
        l1 = df[df["level"] == 1]
        l2 = df[df["level"] == 2]
        assert len(l1) == 2
        assert len(l2) == 4
        # L1 amount check
        assert l1.iloc[0]["amount"] == 850000.0

    def test_none_path(self):
        assert normalize_budget_expenditure_function(None) is None


class TestNormalizeBudgetExpenditureAgency:
    def test_basic(self, sample_expenditure_agency_csv):
        df = normalize_budget_expenditure_agency(sample_expenditure_agency_csv, fiscal_year=115)
        assert df is not None
        assert len(df) == 3
        assert df["agency_name"].iloc[0] == "教育處"
        assert df["amount"].iloc[0] == 2200000.0

    def test_none_path(self):
        assert normalize_budget_expenditure_agency(None) is None
