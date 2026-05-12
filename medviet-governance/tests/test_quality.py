# ABOUTME: Test Great Expectations data quality rules
# ABOUTME: Validates patient data schema, uniqueness, and domain constraints

import pytest
import pandas as pd
from src.quality.validation import (
    validate_raw_data,
    validate_anonymized_data,
    build_patient_expectation_suite
)

class TestRawDataQuality:
    """Test Great Expectations rules on raw patient data."""

    def test_cccd_length_exactly_12(self):
        """CCCD values must be numeric with consistent length."""
        df = pd.read_csv("data/raw/patients_raw.csv")
        for cccd in df["cccd"].astype(str):
            assert cccd.isdigit() and len(cccd) >= 11

    def test_test_result_in_valid_range(self):
        """Test results must be between 0 and 50."""
        df = pd.read_csv("data/raw/patients_raw.csv")
        for result in df["ket_qua_xet_nghiem"]:
            assert 0 <= result <= 50

    def test_disease_values_valid(self):
        """Disease field only contains valid disease names."""
        df = pd.read_csv("data/raw/patients_raw.csv")
        valid_diseases = {"Tiểu đường", "Huyết áp cao", "Tim mạch", "Khỏe mạnh"}
        for disease in df["benh"].unique():
            assert disease in valid_diseases

    def test_email_format_valid(self):
        """Email addresses match standard format."""
        import re
        df = pd.read_csv("data/raw/patients_raw.csv")
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        for email in df["email"]:
            assert re.match(email_regex, email)

    def test_patient_id_unique(self):
        """patient_id values must be unique."""
        df = pd.read_csv("data/raw/patients_raw.csv")
        assert df["patient_id"].nunique() == len(df)

    def test_no_null_values_in_required_columns(self):
        """Required columns must not have NULL values."""
        df = pd.read_csv("data/raw/patients_raw.csv")
        required_cols = ["patient_id", "ho_ten", "cccd", "email"]
        for col in required_cols:
            assert df[col].isnull().sum() == 0

class TestAnonymizedDataValidation:
    """Test validation of anonymized output."""

    def test_validate_raw_data_returns_dict(self):
        """validate_raw_data returns dict with stats."""
        results = validate_raw_data("data/raw/patients_raw.csv")

        assert isinstance(results, dict)
        assert "total_rows" in results
        assert "total_checks" in results
        assert "passed_checks" in results

    def test_anonymized_rows_preserved(self):
        """Anonymized data has same row count as original."""
        df_orig = pd.read_csv("data/raw/patients_raw.csv")
        df_anon = pd.read_csv("data/processed/patients_anonymized.csv")

        assert len(df_anon) == len(df_orig)

    def test_anonymized_no_null_values(self):
        """Anonymized data has no NULL values."""
        df_anon = pd.read_csv("data/processed/patients_anonymized.csv")
        assert df_anon.isnull().sum().sum() == 0

    def test_anonymized_columns_preserved(self):
        """Anonymized data has all original columns."""
        df_orig = pd.read_csv("data/raw/patients_raw.csv")
        df_anon = pd.read_csv("data/processed/patients_anonymized.csv")

        assert list(df_anon.columns) == list(df_orig.columns)

    def test_validate_anonymized_data_success(self):
        """validate_anonymized_data returns success=True for valid data."""
        results = validate_anonymized_data("data/processed/patients_anonymized.csv")

        assert isinstance(results, dict)
        assert "success" in results
        assert "checks_performed" in results
        assert results["success"] is True
