"""Unit tests for etl/validator.py."""
import pandas as pd
import pytest

from etl.validator import validate_table, validate_all, SCHEMAS, ValidationResult


class TestValidateTable:
    """Test individual table validation rules."""

    def test_valid_population_annual(self):
        df = pd.DataFrame({
            "year": [113, 114],
            "total_population": [262000, 261500],
            "male": [127000, 126800],
            "female": [135000, 134700],
            "natural_increase": [-1500, -1800],
            "social_increase": [-500, -200],
            "households": [100000, 100200],
            "growth_pct": ["-0.5%", "-0.2%"],
        })
        result = validate_table("population_annual", df)
        assert result.passed is True
        assert result.row_count == 2

    def test_empty_dataframe(self):
        df = pd.DataFrame()
        result = validate_table("population_annual", df)
        assert result.passed is False
        assert any("empty" in e.lower() for e in result.errors)

    def test_missing_required_column(self):
        df = pd.DataFrame({"year": [113], "total_population": [262000]})
        # Missing male, female
        result = validate_table("population_annual", df)
        assert result.passed is False
        assert any("missing" in e.lower() for e in result.errors)

    def test_null_heavy_column(self):
        df = pd.DataFrame({
            "year": [113, 114, 115],
            "total_population": [262000, None, None],
            "male": [127000, None, None],
            "female": [135000, None, None],
        })
        result = validate_table("population_annual", df)
        assert result.passed is False  # >50% nulls in total_population

    def test_duplicate_rows_warning(self):
        df = pd.DataFrame({
            "year": [113, 113],
            "total_population": [262000, 262000],
            "male": [127000, 127000],
            "female": [135000, 135000],
        })
        result = validate_table("population_annual", df)
        assert any("duplicate" in w.lower() for w in result.warnings)

    def test_out_of_range_warning(self):
        df = pd.DataFrame({
            "year": [113],
            "total_population": [9999999],  # Way above 500k
            "male": [127000],
            "female": [135000],
        })
        result = validate_table("population_annual", df)
        assert any("outside" in w.lower() for w in result.warnings)

    def test_no_schema_defined(self):
        df = pd.DataFrame({"x": [1]})
        result = validate_table("unknown_table", df)
        assert result.passed is True  # No schema = pass with warning
        assert len(result.warnings) > 0

    def test_budget_revenue_valid(self):
        df = pd.DataFrame({
            "fiscal_year": [115, 115, 115],
            "source_category": ["稅課收入", "規費收入", "罰款收入"],
            "amount": [5255680, 180000, 50000],
        })
        result = validate_table("budget_revenue_by_source", df)
        assert result.passed is True

    def test_age_gender_row_count(self):
        df = pd.DataFrame({
            "age_group": ["0~4歲"],
            "male": [3000],
            "female": [2800],
            "total": [5800],
        })
        result = validate_table("population_age_gender", df)
        # Only 1 row, min is 15 → warning
        assert any("row" in w.lower() for w in result.warnings)


class TestValidateAll:
    """Test full validation run against processed data."""

    def test_with_processed_data(self):
        """Run against actual processed CSVs if they exist."""
        results = validate_all()
        assert len(results) > 0
        # All results should be ValidationResult instances
        for r in results:
            assert isinstance(r, ValidationResult)
            assert isinstance(r.passed, bool)
            assert isinstance(r.errors, list)
            assert isinstance(r.warnings, list)

    def test_custom_directory(self, tmp_path):
        """Validate from a custom directory with known test data."""
        df = pd.DataFrame({
            "year": [113],
            "total_population": [262000],
            "male": [127000],
            "female": [135000],
        })
        df.to_csv(tmp_path / "population_annual.csv", index=False)
        results = validate_all(tmp_path)
        assert len(results) == 1
        assert results[0].passed is True
