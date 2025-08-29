"""
Tests for the main Streamlit application
"""

import os
import tempfile
from pathlib import Path

import pandas as pd
import pytest

from src.app.main import ReportProcessor


class TestReportProcessor:
    """Test cases for ReportProcessor class"""

    def setup_method(self):
        """Setup test fixtures"""
        self.processor = ReportProcessor()

        # Create sample data for testing
        self.sample_rpt600_data = {
            "Payee": ["ASC001", "ASC002"],
            "Dealer": ["DLR001", "DLR002"],
            "Commission": [100.00, 150.00],
            "Date": ["2024-10-01", "2024-10-02"],
        }

        self.sample_rpt908_data = {
            "Contract": ["CTR001", "CTR002"],
            "Cancellation_Reason": ["Customer Request", "Non-Payment"],
            "Refund_Amount": [50.00, 75.00],
            "Date": ["2024-10-01", "2024-10-02"],
        }

    def test_processor_initialization(self):
        """Test ReportProcessor initialization"""
        assert self.processor.supported_reports == ["RPT600", "RPT908"]
        assert len(self.processor.processed_reports) == 0

    def test_detect_report_type_rpt600(self):
        """Test RPT600 detection"""
        df = pd.DataFrame(self.sample_rpt600_data)
        report_type = self.processor.detect_report_type(df)
        assert report_type == "RPT600"

    def test_detect_report_type_rpt908(self):
        """Test RPT908 detection"""
        df = pd.DataFrame(self.sample_rpt908_data)
        report_type = self.processor.detect_report_type(df)
        assert report_type == "RPT908"

    def test_validate_report_csv(self):
        """Test CSV file validation"""
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            df = pd.DataFrame(self.sample_rpt600_data)
            df.to_csv(f.name, index=False)
            temp_path = f.name

        try:
            result = self.processor.validate_report(temp_path)
            assert result["valid"] is True
            assert result["report_type"] == "RPT600"
            assert result["row_count"] == 2
        finally:
            os.unlink(temp_path)

    def test_validate_report_excel(self):
        """Test Excel file validation"""
        # Create temporary Excel file
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            df = pd.DataFrame(self.sample_rpt600_data)
            df.to_excel(f.name, index=False)
            temp_path = f.name

        try:
            result = self.processor.validate_report(temp_path)
            assert result["valid"] is True
            assert result["report_type"] == "RPT600"
            assert result["row_count"] == 2
        finally:
            os.unlink(temp_path)

    def test_process_rpt600(self):
        """Test RPT600 processing"""
        df = pd.DataFrame(self.sample_rpt600_data)
        result = self.processor.process_rpt600(df)

        assert result["success"] is True
        assert result["summary"]["total_records"] == 2
        assert result["summary"]["unique_payees"] == 2
        assert result["summary"]["unique_dealers"] == 2
        assert result["summary"]["total_amount"] == 250.00

    def test_process_rpt908(self):
        """Test RPT908 processing"""
        df = pd.DataFrame(self.sample_rpt908_data)
        result = self.processor.process_rpt908(df)

        assert result["success"] is True
        assert result["summary"]["total_records"] == 2
        assert result["summary"]["total_refund_amount"] == 125.00
        assert "Customer Request" in result["summary"]["cancellation_reasons"]

    def test_execute_sop_workflow_rpt600(self):
        """Test SOP workflow for RPT600"""
        df = pd.DataFrame(self.sample_rpt600_data)
        result = self.processor.execute_sop_workflow("RPT600", df)

        assert result["success"] is True
        assert len(self.processor.processed_reports) == 1
        assert self.processor.processed_reports[0]["report_type"] == "RPT600"
        assert self.processor.processed_reports[0]["status"] == "completed"

    def test_execute_sop_workflow_rpt908(self):
        """Test SOP workflow for RPT908"""
        df = pd.DataFrame(self.sample_rpt908_data)
        result = self.processor.execute_sop_workflow("RPT908", df)

        assert result["success"] is True
        assert len(self.processor.processed_reports) == 1
        assert self.processor.processed_reports[0]["report_type"] == "RPT908"
        assert self.processor.processed_reports[0]["status"] == "completed"

    def test_save_processed_data(self):
        """Test saving processed data"""
        df = pd.DataFrame(self.sample_rpt600_data)
        result = self.processor.process_rpt600(df)

        # Test saving
        self.processor.save_processed_data("RPT600", df, result)

        # Check if output directory was created
        output_dir = Path("processed_reports")
        assert output_dir.exists()

        # Clean up
        import shutil

        if output_dir.exists():
            shutil.rmtree(output_dir)

    def test_error_handling_invalid_file(self):
        """Test error handling for invalid files"""
        result = self.processor.validate_report("nonexistent_file.csv")
        assert result["valid"] is False
        assert "Error reading file" in result["error"]

    def test_error_handling_empty_file(self):
        """Test error handling for empty files"""
        # Create empty CSV file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("")
            temp_path = f.name

        try:
            result = self.processor.validate_report(temp_path)
            assert result["valid"] is False
            assert "Error reading file" in result["error"]
        finally:
            os.unlink(temp_path)


def test_health_check():
    """Test that the application can be imported and initialized"""
    try:
        from src.app.main import ReportProcessor

        processor = ReportProcessor()
        assert processor is not None
    except ImportError as e:
        pytest.fail(f"Failed to import main application: {e}")
