"""Integration test — end-to-end pipeline with synthetic data."""
import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import patch

from etl.normalizer import run_normalization
from etl.validator import validate_all


class TestPipelineIntegration:
    """Test normalizer → validator pipeline with real-ish data."""

    def test_full_normalization_with_raw_data(self, tmp_path):
        """Simulate raw → processed pipeline."""
        raw_dir = tmp_path / "data" / "raw"
        processed_dir = tmp_path / "data" / "processed"
        raw_dir.mkdir(parents=True)

        # Create minimal raw data
        pop = pd.DataFrame({
            "年度": [113, 114],
            "total": [262000, 261500],
            "male": [127000, 126800],
            "female": [135000, 134700],
            "households": [100000, 100200],
            "growth_pct": ["-0.5%", "-0.2%"],
        })
        pop.to_csv(raw_dir / "population_historical.csv", index=False)

        revenue = pd.DataFrame({
            "款": ["1", "2", "3"],
            "科目名稱": ["稅課收入", "規費收入", "罰款收入"],
            "經常門（千元）": ["5255680", "180000", "50000"],
            "資本門（千元）": ["-", "-", "-"],
            "合計（千元）": ["5255680", "180000", "50000"],
        })
        revenue.to_csv(raw_dir / "budget_revenue_115.csv", index=False)

        agency = pd.DataFrame({
            "名稱": ["教育處", "社會處"],
            "合計金額": ["2200000", "1800000"],
        })
        agency.to_csv(raw_dir / "budget_expenditure_dept_115.csv", index=False)

        # Patch global dirs to use tmp_path
        with patch("etl.normalizer.RAW_DIR", raw_dir), \
             patch("etl.normalizer.PROCESSED_DIR", processed_dir):
            results = run_normalization()

        # At least population_annual and budget_revenue_by_source should succeed
        assert results.get("population_annual") is not None
        assert results.get("budget_revenue_by_source") is not None
        assert results.get("budget_expenditure_by_agency") is not None

        # Validate the processed output
        val_raw = pd.read_csv(processed_dir / "population_annual.csv")
        assert len(val_raw) == 2
        assert val_raw["total_population"].iloc[0] == 262000

    def test_validator_catches_bad_data(self, tmp_path):
        """Validator should flag a table with missing columns."""
        bad_df = pd.DataFrame({"wrong_col": [1, 2, 3]})
        bad_df.to_csv(tmp_path / "population_annual.csv", index=False)

        results = validate_all(tmp_path)
        pop_result = [r for r in results if r.table == "population_annual"][0]
        assert pop_result.passed is False
        assert any("missing" in e.lower() for e in pop_result.errors)


class TestFetcherRetry:
    """Test that fetcher retry logic works (mocked HTTP)."""

    def test_retry_succeeds_on_second_attempt(self):
        """Mock requests to fail once then succeed."""
        from etl.fetcher import _request_with_retry
        from unittest.mock import MagicMock, patch
        import requests

        ok_resp = MagicMock()
        ok_resp.text = "header1,header2\nval1,val2\n"
        ok_resp.raise_for_status = MagicMock()

        with patch("etl.fetcher.requests.request") as mock_req, \
             patch("time.sleep") as mock_sleep:
            mock_req.side_effect = [requests.ConnectionError("timeout"), ok_resp]
            result = _request_with_retry("test", 3, "GET", "http://example.com")

        assert result is not None
        assert "val1" in result
        mock_sleep.assert_called_once_with(2)

    def test_retry_exhausted(self):
        """All retries fail → returns None."""
        from etl.fetcher import _request_with_retry
        from unittest.mock import patch
        import requests

        with patch("etl.fetcher.requests.request", side_effect=requests.ConnectionError("down")), \
             patch("time.sleep"):
            result = _request_with_retry("test", 2, "GET", "http://example.com")

        assert result is None
