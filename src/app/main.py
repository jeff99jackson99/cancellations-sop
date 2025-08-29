"""
Main Streamlit application for RPT 600 and RPT 908 SOP processing
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional

import pandas as pd
import streamlit as st

from .config import config
from .utils import create_output_directory, format_currency, setup_logging

# Configure logging
setup_logging(config.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title=config.APP_NAME,
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


class ReportProcessor:
    """Handles processing of RPT 600 and RPT 908 reports"""

    def __init__(self):
        self.supported_reports = ["RPT600", "RPT908"]
        self.processed_reports = []

    def validate_report(self, file_path: str) -> Dict[str, Any]:
        """Validate uploaded report file"""
        try:
            # Check file extension
            if file_path.endswith(".csv"):
                df = pd.read_csv(file_path)
            elif file_path.endswith(".xlsx"):
                df = pd.read_excel(file_path)
            else:
                return {
                    "valid": False,
                    "error": "Unsupported file format. Please upload CSV or Excel files.",
                }

            # Basic validation
            if df.empty:
                return {"valid": False, "error": "File appears to be empty"}

            # Check for required columns based on report type
            report_type = self.detect_report_type(df)
            if not report_type:
                return {"valid": False, "error": "Could not determine report type"}

            return {
                "valid": True,
                "report_type": report_type,
                "row_count": len(df),
                "columns": list(df.columns),
            }

        except Exception as e:
            logger.error(f"Error validating report: {str(e)}")
            return {"valid": False, "error": f"Error reading file: {str(e)}"}

    def detect_report_type(self, df: pd.DataFrame) -> Optional[str]:
        """Detect if this is RPT600 or RPT908 based on column structure"""
        columns = [col.lower() for col in df.columns]

        # RPT600 typically has payee-related columns
        rpt600_indicators = ["payee", "commission", "dealer", "fee"]
        # RPT908 typically has cancellation-related columns
        rpt908_indicators = ["cancellation", "cancel", "termination", "refund"]

        rpt600_score = sum(
            1
            for indicator in rpt600_indicators
            if any(indicator in col for col in columns)
        )
        rpt908_score = sum(
            1
            for indicator in rpt908_indicators
            if any(indicator in col for col in columns)
        )

        if rpt600_score > rpt908_score:
            return "RPT600"
        elif rpt908_score > rpt600_score:
            return "RPT908"
        else:
            return None

    def process_rpt600(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Process RPT600 Payee Statement report"""
        try:
            # Extract key information
            summary = {
                "total_records": len(df),
                "unique_payees": (
                    df.get("Payee", df.get("Payee Number", pd.Series())).nunique()
                    if "Payee" in df.columns or "Payee Number" in df.columns
                    else 0
                ),
                "unique_dealers": (
                    df.get("Dealer", df.get("Dealer Number", pd.Series())).nunique()
                    if "Dealer" in df.columns or "Dealer Number" in df.columns
                    else 0
                ),
                "date_range": None,
                "total_amount": 0,
            }

            # Try to find date columns and amount columns
            date_cols = [
                col
                for col in df.columns
                if "date" in col.lower() or "time" in col.lower()
            ]
            amount_cols = [
                col
                for col in df.columns
                if "amount" in col.lower()
                or "commission" in col.lower()
                or "fee" in col.lower()
            ]

            if date_cols:
                try:
                    dates = pd.to_datetime(df[date_cols[0]], errors="coerce")
                    summary["date_range"] = (
                        f"{dates.min().strftime('%Y-%m-%d')} to {dates.max().strftime('%Y-%m-%d')}"
                    )
                except:
                    pass

            if amount_cols:
                try:
                    summary["total_amount"] = df[amount_cols[0]].sum()
                except:
                    pass

            return {
                "success": True,
                "summary": summary,
                "data": df.head(100).to_dict("records"),  # First 100 rows for preview
            }

        except Exception as e:
            logger.error(f"Error processing RPT600: {str(e)}")
            return {"success": False, "error": str(e)}

    def process_rpt908(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Process RPT908 Cancellation report"""
        try:
            # Extract key information
            summary = {
                "total_records": len(df),
                "cancellation_reasons": {},
                "total_refund_amount": 0,
                "date_range": None,
            }

            # Try to find cancellation reason column
            reason_cols = [
                col
                for col in df.columns
                if "reason" in col.lower() or "cause" in col.lower()
            ]
            if reason_cols:
                summary["cancellation_reasons"] = (
                    df[reason_cols[0]].value_counts().to_dict()
                )

            # Try to find refund amount column
            refund_cols = [
                col
                for col in df.columns
                if "refund" in col.lower() or "amount" in col.lower()
            ]
            if refund_cols:
                try:
                    summary["total_refund_amount"] = df[refund_cols[0]].sum()
                except:
                    pass

            return {
                "success": True,
                "summary": summary,
                "data": df.head(100).to_dict("records"),  # First 100 rows for preview
            }

        except Exception as e:
            logger.error(f"Error processing RPT908: {str(e)}")
            return {"success": False, "error": str(e)}

    def execute_sop_workflow(
        self, report_type: str, df: pd.DataFrame
    ) -> Dict[str, Any]:
        """Execute the SOP workflow based on report type"""
        try:
            if report_type == "RPT600":
                result = self.process_rpt600(df)
            elif report_type == "RPT908":
                result = self.process_rpt908(df)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported report type: {report_type}",
                }

            if result["success"]:
                # Log the processing
                self.processed_reports.append(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "report_type": report_type,
                        "records_processed": result["summary"]["total_records"],
                        "status": "completed",
                    }
                )

                # Save processed data
                self.save_processed_data(report_type, df, result)

            return result

        except Exception as e:
            logger.error(f"Error in SOP workflow: {str(e)}")
            return {"success": False, "error": str(e)}

    def save_processed_data(
        self, report_type: str, df: pd.DataFrame, result: Dict[str, Any]
    ):
        """Save processed data to output directory"""
        try:
            output_dir = create_output_directory(config.OUTPUT_DIRECTORY)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{report_type}_{timestamp}.xlsx"

            # Save processed data
            with pd.ExcelWriter(output_dir / filename, engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name="Raw_Data", index=False)

                # Create summary sheet
                summary_df = pd.DataFrame([result["summary"]])
                summary_df.to_excel(writer, sheet_name="Summary", index=False)

                # Create processing log sheet
                log_df = pd.DataFrame(self.processed_reports)
                log_df.to_excel(writer, sheet_name="Processing_Log", index=False)

            logger.info(f"Processed data saved to {filename}")

        except Exception as e:
            logger.error(f"Error saving processed data: {str(e)}")


def main():
    """Main Streamlit application"""
    st.title(f"📊 {config.APP_NAME}")
    st.markdown(f"**Version:** {config.APP_VERSION}")
    st.markdown("Automated processing for RPT 600 and RPT 908 reports")

    # Initialize processor
    if "processor" not in st.session_state:
        st.session_state.processor = ReportProcessor()

    # Sidebar
    st.sidebar.header("Report Upload")
    uploaded_file = st.sidebar.file_uploader(
        "Choose a report file",
        type=["csv", "xlsx"],
        help="Upload RPT600 or RPT908 report files",
    )

    # Configuration info
    with st.sidebar.expander("Configuration"):
        config_summary = config.get_config_summary()
        for key, value in config_summary.items():
            st.text(f"{key}: {value}")

    # Main content area
    if uploaded_file is not None:
        st.header("Report Processing")

        # Save uploaded file temporarily
        temp_path = f"temp_{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        try:
            # Validate report
            validation_result = st.session_state.processor.validate_report(temp_path)

            if validation_result["valid"]:
                st.success("✅ File validated successfully!")
                st.info(f"**Report Type:** {validation_result['report_type']}")
                st.info(f"**Records:** {validation_result['row_count']:,}")
                st.info(
                    f"**Columns:** {', '.join(validation_result['columns'][:10])}{'...' if len(validation_result['columns']) > 10 else ''}"
                )

                # Process button
                if st.button("🚀 Process Report", type="primary"):
                    with st.spinner("Processing report..."):
                        # Read the file
                        if uploaded_file.name.endswith(".csv"):
                            df = pd.read_csv(temp_path)
                        else:
                            df = pd.read_excel(temp_path)

                        # Execute SOP workflow
                        result = st.session_state.processor.execute_sop_workflow(
                            validation_result["report_type"], df
                        )

                        if result["success"]:
                            st.success("✅ Report processed successfully!")

                            # Display summary
                            st.subheader("Processing Summary")
                            summary = result["summary"]

                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric(
                                    "Total Records", f"{summary['total_records']:,}"
                                )
                                if "unique_payees" in summary:
                                    st.metric("Unique Payees", summary["unique_payees"])
                                if "unique_dealers" in summary:
                                    st.metric(
                                        "Unique Dealers", summary["unique_dealers"]
                                    )

                            with col2:
                                if (
                                    "total_amount" in summary
                                    and summary["total_amount"] > 0
                                ):
                                    st.metric(
                                        "Total Amount",
                                        format_currency(summary["total_amount"]),
                                    )
                                if (
                                    "total_refund_amount" in summary
                                    and summary["total_refund_amount"] > 0
                                ):
                                    st.metric(
                                        "Total Refund Amount",
                                        format_currency(summary["total_refund_amount"]),
                                    )
                                if "date_range" in summary and summary["date_range"]:
                                    st.metric("Date Range", summary["date_range"])

                            # Display preview data
                            st.subheader("Data Preview")
                            preview_df = pd.DataFrame(result["data"])
                            st.dataframe(preview_df, use_container_width=True)

                        else:
                            st.error(f"❌ Processing failed: {result['error']}")

            else:
                st.error(f"❌ File validation failed: {validation_result['error']}")

        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
            logger.error(f"Error in main: {str(e)}")

        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)

    else:
        st.info("👆 Please upload a report file using the sidebar")

        # Display processing history
        if st.session_state.processor.processed_reports:
            st.subheader("Processing History")
            history_df = pd.DataFrame(st.session_state.processor.processed_reports)
            st.dataframe(history_df, use_container_width=True)

    # Footer
    st.markdown("---")
    st.markdown(f"**{config.APP_NAME}** | Built with Streamlit")


if __name__ == "__main__":
    main()
