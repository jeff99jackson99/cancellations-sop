"""
Configuration management for the Cancellations SOP Processor
"""

import os
from typing import Any, Dict, List

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration class"""

    # Application settings
    APP_NAME = "Cancellations SOP Processor"
    APP_VERSION = "0.1.0"
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"

    # Server settings
    SERVER_PORT = int(os.getenv("STREAMLIT_SERVER_PORT", "8501"))
    SERVER_ADDRESS = os.getenv("STREAMLIT_SERVER_ADDRESS", "0.0.0.0")
    SERVER_HEADLESS = os.getenv("STREAMLIT_SERVER_HEADLESS", "false").lower() == "true"

    # File processing settings
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE", "100"))
    SUPPORTED_FORMATS = os.getenv("SUPPORTED_FORMATS", "csv,xlsx").split(",")
    ALLOWED_FILE_TYPES = [f".{fmt.strip()}" for fmt in SUPPORTED_FORMATS]

    # Output settings
    OUTPUT_DIRECTORY = os.getenv("OUTPUT_DIRECTORY", "processed_reports")
    ENABLE_EXCEL_EXPORT = os.getenv("ENABLE_EXCEL_EXPORT", "true").lower() == "true"
    ENABLE_CSV_EXPORT = os.getenv("ENABLE_CSV_EXPORT", "true").lower() == "true"

    # Logging settings
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "cancellations_sop.log")

    # Security settings
    ENABLE_FILE_UPLOAD = os.getenv("ENABLE_FILE_UPLOAD", "true").lower() == "true"
    MAX_UPLOAD_FILES = int(os.getenv("MAX_UPLOAD_FILES", "10"))

    # Processing settings
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", "1000"))
    ENABLE_VALIDATION = os.getenv("ENABLE_VALIDATION", "true").lower() == "true"
    ENABLE_BACKUP = os.getenv("ENABLE_BACKUP", "true").lower() == "true"

    # Report-specific settings
    RPT600_SETTINGS = {
        "required_columns": ["Payee", "Dealer", "Commission"],
        "optional_columns": ["Date", "Fee_Category", "Product_Type", "State"],
        "amount_columns": ["Commission", "Fee", "Amount"],
        "date_columns": ["Date", "Transaction_Date", "Billing_Date"],
    }

    RPT908_SETTINGS = {
        "required_columns": ["Contract", "Cancellation_Reason"],
        "optional_columns": ["Date", "Dealer", "Product_Type", "Refund_Amount"],
        "amount_columns": ["Refund_Amount", "Amount", "Fee"],
        "date_columns": ["Date", "Cancellation_Date", "Termination_Date"],
    }

    @classmethod
    def get_report_settings(cls, report_type: str) -> Dict[str, Any]:
        """Get settings for specific report type"""
        if report_type == "RPT600":
            return cls.RPT600_SETTINGS
        elif report_type == "RPT908":
            return cls.RPT908_SETTINGS
        else:
            return {}

    @classmethod
    def validate_config(cls) -> List[str]:
        """Validate configuration and return any errors"""
        errors = []

        # Check required directories
        if not os.path.exists(cls.OUTPUT_DIRECTORY):
            try:
                os.makedirs(cls.OUTPUT_DIRECTORY, exist_ok=True)
            except Exception as e:
                errors.append(f"Cannot create output directory: {e}")

        # Validate file size limit
        if cls.MAX_FILE_SIZE_MB <= 0:
            errors.append("MAX_FILE_SIZE must be positive")

        # Validate batch size
        if cls.BATCH_SIZE <= 0:
            errors.append("BATCH_SIZE must be positive")

        # Validate server port
        if not (1024 <= cls.SERVER_PORT <= 65535):
            errors.append("SERVER_PORT must be between 1024 and 65535")

        return errors

    @classmethod
    def get_config_summary(cls) -> Dict[str, Any]:
        """Get configuration summary for display"""
        return {
            "app_name": cls.APP_NAME,
            "app_version": cls.APP_VERSION,
            "server_port": cls.SERVER_PORT,
            "server_address": cls.SERVER_ADDRESS,
            "max_file_size_mb": cls.MAX_FILE_SIZE_MB,
            "supported_formats": cls.SUPPORTED_FORMATS,
            "output_directory": cls.OUTPUT_DIRECTORY,
            "enable_validation": cls.ENABLE_VALIDATION,
            "enable_backup": cls.ENABLE_BACKUP,
        }


# Global configuration instance
config = Config()
