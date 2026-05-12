

# ABOUTME: Great Expectations data quality validation suite
# ABOUTME: Validates raw and anonymized patient data integrity

import pandas as pd
import re

def validate_raw_data(csv_path: str) -> dict:
    """Validate raw patient data against Great Expectations rules."""
    df = pd.read_csv(csv_path)

    results = {
        "total_rows": len(df),
        "total_checks": 0,
        "passed_checks": 0,
        "failed_checks": []
    }

    # Check 1: CCCD format (numeric, >= 11 digits)
    for idx, cccd in enumerate(df["cccd"].astype(str)):
        results["total_checks"] += 1
        if cccd.isdigit() and len(cccd) >= 11:
            results["passed_checks"] += 1
        else:
            results["failed_checks"].append(f"Row {idx}: CCCD invalid: {cccd}")

    # Check 2: Test result range
    for idx, result in enumerate(df["ket_qua_xet_nghiem"]):
        results["total_checks"] += 1
        if 0 <= result <= 50:
            results["passed_checks"] += 1
        else:
            results["failed_checks"].append(f"Row {idx}: Test result out of range: {result}")

    # Check 3: Valid diseases
    valid_diseases = {"Tiểu đường", "Huyết áp cao", "Tim mạch", "Khỏe mạnh"}
    for idx, disease in enumerate(df["benh"]):
        results["total_checks"] += 1
        if disease in valid_diseases:
            results["passed_checks"] += 1
        else:
            results["failed_checks"].append(f"Row {idx}: Invalid disease: {disease}")

    # Check 4: Email format
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    for idx, email in enumerate(df["email"]):
        results["total_checks"] += 1
        if re.match(email_regex, str(email)):
            results["passed_checks"] += 1
        else:
            results["failed_checks"].append(f"Row {idx}: Invalid email: {email}")

    # Check 5: Unique patient IDs
    results["total_checks"] += 1
    if df["patient_id"].nunique() == len(df):
        results["passed_checks"] += 1
    else:
        results["failed_checks"].append("Duplicate patient IDs found")

    # Check 6: No nulls in required columns
    required_cols = ["patient_id", "ho_ten", "cccd", "email"]
    for col in required_cols:
        results["total_checks"] += 1
        null_count = df[col].isnull().sum()
        if null_count == 0:
            results["passed_checks"] += 1
        else:
            results["failed_checks"].append(f"Column {col}: {null_count} NULL values")

    results["success"] = len(results["failed_checks"]) == 0
    results["pass_rate"] = results["passed_checks"] / results["total_checks"] if results["total_checks"] > 0 else 0

    return results

def validate_anonymized_data(csv_path: str) -> dict:
    """Validate anonymized patient data integrity."""
    df = pd.read_csv(csv_path)

    results = {
        "total_rows": len(df),
        "checks_performed": 0,
        "passed_checks": 0,
        "failed_checks": [],
        "stats": {
            "null_count": df.isnull().sum().sum(),
            "duplicate_rows": len(df) - len(df.drop_duplicates()),
            "columns": list(df.columns)
        }
    }

    # Check 1: No NULL values
    results["checks_performed"] += 1
    if df.isnull().sum().sum() == 0:
        results["passed_checks"] += 1
    else:
        results["failed_checks"].append("NULL values found in anonymized data")

    # Check 2: All columns present
    results["checks_performed"] += 1
    expected_cols = [
        "patient_id", "ho_ten", "cccd", "ngay_sinh", "so_dien_thoai",
        "email", "dia_chi", "benh", "ket_qua_xet_nghiem",
        "bac_si_phu_trach", "ngay_kham"
    ]
    if set(df.columns) == set(expected_cols):
        results["passed_checks"] += 1
    else:
        results["failed_checks"].append("Missing or extra columns")

    # Check 3: patient_id still unique
    results["checks_performed"] += 1
    if df["patient_id"].nunique() == len(df):
        results["passed_checks"] += 1
    else:
        results["failed_checks"].append("Duplicate patient_ids after anonymization")

    # Check 4: Row count preserved
    df_orig = pd.read_csv("data/raw/patients_raw.csv")
    results["checks_performed"] += 1
    if len(df) == len(df_orig):
        results["passed_checks"] += 1
    else:
        results["failed_checks"].append(f"Row count changed: {len(df_orig)} → {len(df)}")

    results["success"] = len(results["failed_checks"]) == 0
    return results

def build_patient_expectation_suite() -> dict:
    """Define Great Expectations suite for patient data."""
    expectations = {
        "dataset_name": "patient_data",
        "expectations": [
            {
                "expectation_type": "expect_table_row_count_to_equal",
                "kwargs": {"value": 200}
            },
            {
                "expectation_type": "expect_column_values_to_be_of_type",
                "kwargs": {"column": "patient_id", "type_": "str"}
            },
            {
                "expectation_type": "expect_column_values_to_match_regex",
                "kwargs": {"column": "cccd", "regex": "^\\d{12}$"}
            },
            {
                "expectation_type": "expect_column_values_to_match_regex",
                "kwargs": {"column": "so_dien_thoai", "regex": "^0[3578]\\d{8}$"}
            },
            {
                "expectation_type": "expect_column_values_to_match_regex",
                "kwargs": {"column": "email",
                          "regex": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"}
            },
            {
                "expectation_type": "expect_column_values_to_be_in_set",
                "kwargs": {"column": "benh",
                          "value_set": ["Tiểu đường", "Huyết áp cao", "Tim mạch", "Khỏe mạnh"]}
            },
            {
                "expectation_type": "expect_column_values_to_be_between",
                "kwargs": {"column": "ket_qua_xet_nghiem", "min_value": 0, "max_value": 50}
            },
            {
                "expectation_type": "expect_column_values_to_not_be_null",
                "kwargs": {"column": "patient_id"}
            },
            {
                "expectation_type": "expect_column_values_to_be_unique",
                "kwargs": {"column": "patient_id"}
            }
        ]
    }
    return expectations
