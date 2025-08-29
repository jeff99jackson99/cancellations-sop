"""
Pytest configuration and fixtures
"""

import os
import tempfile
from pathlib import Path

import pandas as pd
import pytest


@pytest.fixture
def sample_rpt600_data():
    """Sample RPT600 data for testing"""
    return {
        "Payee": ["ASC001", "ASC002", "ASC003"],
        "Dealer": ["DLR001", "DLR002", "DLR001"],
        "Commission": [100.00, 150.00, 200.00],
        "Fee_Category": ["Commission", "Commission", "Commission"],
        "Date": ["2024-10-01", "2024-10-02", "2024-10-03"],
        "Product_Type": ["Warranty", "Service", "Warranty"],
        "State": ["AZ", "CA", "AZ"],
    }


@pytest.fixture
def sample_rpt908_data():
    """Sample RPT908 data for testing"""
    return {
        "Contract": ["CTR001", "CTR002", "CTR003"],
        "Cancellation_Reason": ["Customer Request", "Non-Payment", "Service Issue"],
        "Refund_Amount": [50.00, 75.00, 100.00],
        "Date": ["2024-10-01", "2024-10-02", "2024-10-03"],
        "Dealer": ["DLR001", "DLR002", "DLR003"],
        "Product_Type": ["Warranty", "Service", "Warranty"],
    }


@pytest.fixture
def temp_csv_file(sample_rpt600_data):
    """Create temporary CSV file for testing"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        df = pd.DataFrame(sample_rpt600_data)
        df.to_csv(f.name, index=False)
        yield f.name
        os.unlink(f.name)


@pytest.fixture
def temp_excel_file(sample_rpt600_data):
    """Create temporary Excel file for testing"""
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
        df = pd.DataFrame(sample_rpt600_data)
        df.to_excel(f.name, index=False)
        yield f.name
        os.unlink(f.name)


@pytest.fixture
def output_directory():
    """Create and clean up output directory for testing"""
    output_dir = Path("test_processed_reports")
    output_dir.mkdir(exist_ok=True)
    yield output_dir
    # Cleanup
    import shutil

    if output_dir.exists():
        shutil.rmtree(output_dir)
