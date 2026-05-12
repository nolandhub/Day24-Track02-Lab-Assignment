# ABOUTME: Test data generation for Vietnamese patient records
# ABOUTME: Verifies Faker produces valid fake patient data

import pytest
import pandas as pd
import os

def test_generate_patients_creates_csv():
    """Generated CSV exists with correct columns and 200 rows."""
    if os.path.exists("data/raw/patients_raw.csv"):
        os.remove("data/raw/patients_raw.csv")

    os.system("python scripts/generate_data.py")

    assert os.path.exists("data/raw/patients_raw.csv"), "CSV not created"
    df = pd.read_csv("data/raw/patients_raw.csv")

    required_cols = [
        "patient_id", "ho_ten", "cccd", "ngay_sinh", "so_dien_thoai",
        "email", "dia_chi", "benh", "ket_qua_xet_nghiem",
        "bac_si_phu_trach", "ngay_kham"
    ]
    assert list(df.columns) == required_cols, f"Columns don't match"
    assert len(df) == 200, f"Expected 200 rows, got {len(df)}"
    assert df.isnull().sum().sum() == 0, "NULL values found"

def test_cccd_format_valid():
    """CCCD phải là số, ít nhất 10 chữ số."""
    df = pd.read_csv("data/raw/patients_raw.csv")
    for cccd in df["cccd"]:
        assert len(str(cccd)) >= 10, f"CCCD {cccd} too short"
        assert str(cccd).isdigit()

def test_phone_format_valid():
    """Phone phải là số, ít nhất 9 chữ số."""
    df = pd.read_csv("data/raw/patients_raw.csv")
    for phone in df["so_dien_thoai"]:
        assert len(str(phone)) >= 9, f"Phone {phone} too short"
        assert str(phone).isdigit()

def test_ngay_sinh_format_valid():
    """ngay_sinh phải định dạng YYYY-MM-DD."""
    df = pd.read_csv("data/raw/patients_raw.csv")
    import re
    pattern = r"^\d{4}-\d{2}-\d{2}$|^\d{2}/\d{2}/\d{4}$"
    for date in df["ngay_sinh"]:
        assert re.match(pattern, str(date)), f"Invalid date: {date}"

def test_disease_values_valid():
    """benh chỉ chứa các giá trị hợp lệ."""
    df = pd.read_csv("data/raw/patients_raw.csv")
    valid_diseases = {"Tiểu đường", "Huyết áp cao", "Tim mạch", "Khỏe mạnh"}
    for disease in df["benh"].unique():
        assert disease in valid_diseases, f"Invalid disease: {disease}"

def test_test_result_in_range():
    """ket_qua_xet_nghiem trong range [0, 50]."""
    df = pd.read_csv("data/raw/patients_raw.csv")
    for result in df["ket_qua_xet_nghiem"]:
        assert 0 <= result <= 50, f"Result {result} out of range"

def test_patient_id_unique():
    """patient_id phải unique."""
    df = pd.read_csv("data/raw/patients_raw.csv")
    assert df["patient_id"].nunique() == len(df), "Duplicate IDs found"
