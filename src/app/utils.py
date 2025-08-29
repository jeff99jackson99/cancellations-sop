"""
Utility functions for the Cancellations SOP Processor
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

logger = logging.getLogger(__name__)


def setup_logging(log_level: str = "INFO") -> None:
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("cancellations_sop.log"),
            logging.StreamHandler(),
        ],
    )


def validate_file_size(file_path: str, max_size_mb: int = 100) -> bool:
    """Validate file size"""
    try:
        file_size = Path(file_path).stat().st_size
        max_size_bytes = max_size_mb * 1024 * 1024
        return file_size <= max_size_bytes
    except Exception as e:
        logger.error(f"Error checking file size: {e}")
        return False


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations"""
    import re

    # Remove or replace unsafe characters
    safe_filename = re.sub(r'[<>:"/\\|?*]', "_", filename)
    # Limit length
    if len(safe_filename) > 255:
        safe_filename = safe_filename[:255]
    return safe_filename


def create_output_directory(base_path: str = "processed_reports") -> Path:
    """Create output directory if it doesn't exist"""
    output_dir = Path(base_path)
    output_dir.mkdir(exist_ok=True)
    return output_dir


def save_processing_summary(
    output_dir: Path, report_type: str, summary: Dict[str, Any], timestamp: str
) -> Path:
    """Save processing summary to JSON file"""
    summary_file = output_dir / f"{report_type}_summary_{timestamp}.json"

    try:
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2, default=str)
        logger.info(f"Processing summary saved to {summary_file}")
        return summary_file
    except Exception as e:
        logger.error(f"Error saving processing summary: {e}")
        raise


def load_processing_summary(summary_file: Path) -> Optional[Dict[str, Any]]:
    """Load processing summary from JSON file"""
    try:
        with open(summary_file) as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading processing summary: {e}")
        return None


def format_currency(amount: float) -> str:
    """Format amount as currency string"""
    try:
        return f"${amount:,.2f}"
    except (ValueError, TypeError):
        return "$0.00"


def format_date(date_str: str) -> str:
    """Format date string consistently"""
    try:
        if pd.isna(date_str):
            return "N/A"
        # Try to parse and format the date
        parsed_date = pd.to_datetime(date_str, errors="coerce")
        if pd.isna(parsed_date):
            return str(date_str)
        return parsed_date.strftime("%Y-%m-%d")
    except Exception:
        return str(date_str)


def calculate_percentage(numerator: float, denominator: float) -> float:
    """Calculate percentage safely"""
    try:
        if denominator == 0:
            return 0.0
        return (numerator / denominator) * 100
    except (ValueError, TypeError):
        return 0.0


def get_file_extension(file_path: str) -> str:
    """Get file extension from file path"""
    return Path(file_path).suffix.lower()


def is_supported_format(file_path: str, supported_formats: list = None) -> bool:
    """Check if file format is supported"""
    if supported_formats is None:
        supported_formats = [".csv", ".xlsx"]

    file_ext = get_file_extension(file_path)
    return file_ext in supported_formats


def create_backup_file(original_path: str) -> str:
    """Create a backup of the original file"""
    try:
        original_file = Path(original_path)
        backup_path = original_file.with_suffix(f"{original_file.suffix}.backup")

        import shutil

        shutil.copy2(original_file, backup_path)
        logger.info(f"Backup created at {backup_path}")
        return str(backup_path)
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        raise
