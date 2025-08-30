"""
Streamlit Cloud entry point for Cancellations SOP Processor
This file is specifically designed for Streamlit Cloud deployment
"""

import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, Optional

import pandas as pd
import streamlit as st

# Add the src/app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'app'))

# Now import the modules
from config import config
from utils import create_output_directory, format_currency, setup_logging

# Configure logging
setup_logging(config.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Configure Streamlit page
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
        
        # More comprehensive indicators for RPT600 (Payee Statement)
        rpt600_indicators = [
            "payee", "commission", "dealer", "fee", "amount", "payment",
            "earnings", "compensation", "bonus", "incentive", "revenue",
            "payee number", "dealer number", "agent", "representative"
        ]
        
        # More comprehensive indicators for RPT908 (Cancellation Report)
        rpt908_indicators = [
            "cancellation", "cancel", "termination", "refund", "contract",
            "policy", "agreement", "discontinuation", "cessation", "end date",
            "cancellation reason", "termination reason", "refund amount",
            "cancellation date", "termination date"
        ]
        
        # Calculate scores with more flexible matching
        rpt600_score = 0
        rpt908_score = 0
        
        for col in columns:
            # Check for exact matches and partial matches
            for indicator in rpt600_indicators:
                if indicator in col or col in indicator:
                    rpt600_score += 1
                    
            for indicator in rpt908_indicators:
                if indicator in col or col in indicator:
                    rpt908_score += 1
        
        # Add bonus points for very specific indicators
        if any("payee" in col for col in columns):
            rpt600_score += 2
        if any("commission" in col for col in columns):
            rpt600_score += 2
        if any("cancellation" in col for col in columns):
            rpt908_score += 2
        if any("refund" in col for col in columns):
            rpt908_score += 2
            
        # Debug information (you can remove this in production)
        st.sidebar.write(f"Debug - RPT600 Score: {rpt600_score}, RPT908 Score: {rpt908_score}")
        
        # Determine report type with a threshold
        if rpt600_score > rpt908_score and rpt600_score >= 1:
            return "RPT600"
        elif rpt908_score > rpt600_score and rpt908_score >= 1:
            return "RPT908"
        else:
            return None

    def process_rpt600(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Process RPT600 Payee Statement report"""
        try:
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
    
    # Tabbed interface for different upload methods
    upload_tab1, upload_tab2 = st.sidebar.tabs(["📁 Multiple Files", "🏷️ Named Uploads"])
    
    with upload_tab1:
        uploaded_files = st.file_uploader(
            "Choose report files (you can select multiple)",
            type=["csv", "xlsx"],
            accept_multiple_files=True,
            help="Upload multiple RPT600 or RPT908 report files. You can select several files at once."
        )
    
    with upload_tab2:
        st.markdown("**Upload files with specific names:**")
        
        # Named upload sections
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**RPT600 Files:**")
            rpt600_file1 = st.file_uploader(
                "RPT600 - Payee Statement 1",
                type=["csv", "xlsx"],
                key="rpt600_1",
                help="Upload first RPT600 file"
            )
            rpt600_file2 = st.file_uploader(
                "RPT600 - Payee Statement 2", 
                type=["csv", "xlsx"],
                key="rpt600_2",
                help="Upload second RPT600 file"
            )
            rpt600_file3 = st.file_uploader(
                "RPT600 - Payee Statement 3",
                type=["csv", "xlsx"], 
                key="rpt600_3",
                help="Upload third RPT600 file"
            )
        
        with col2:
            st.markdown("**RPT908 Files:**")
            rpt908_file1 = st.file_uploader(
                "RPT908 - Cancellation 1",
                type=["csv", "xlsx"],
                key="rpt908_1",
                help="Upload first RPT908 file"
            )
            rpt908_file2 = st.file_uploader(
                "RPT908 - Cancellation 2",
                type=["csv", "xlsx"],
                key="rpt908_2", 
                help="Upload second RPT908 file"
            )
            rpt908_file3 = st.file_uploader(
                "RPT908 - Cancellation 3",
                type=["csv", "xlsx"],
                key="rpt908_3",
                help="Upload third RPT908 file"
            )
        
        # Additional named uploads
        st.markdown("**Other Files:**")
        other_file1 = st.file_uploader(
            "Additional Report 1",
            type=["csv", "xlsx"],
            key="other_1",
            help="Upload any other report file"
        )
        other_file2 = st.file_uploader(
            "Additional Report 2", 
            type=["csv", "xlsx"],
            key="other_2",
            help="Upload any other report file"
        )
        
        # Collect all named files
        named_files = []
        if rpt600_file1:
            named_files.append(("RPT600 - Payee Statement 1", rpt600_file1, "RPT600"))
        if rpt600_file2:
            named_files.append(("RPT600 - Payee Statement 2", rpt600_file2, "RPT600"))
        if rpt600_file3:
            named_files.append(("RPT600 - Payee Statement 3", rpt600_file3, "RPT600"))
        if rpt908_file1:
            named_files.append(("RPT908 - Cancellation 1", rpt908_file1, "RPT908"))
        if rpt908_file2:
            named_files.append(("RPT908 - Cancellation 2", rpt908_file2, "RPT908"))
        if rpt908_file3:
            named_files.append(("RPT908 - Cancellation 3", rpt908_file3, "RPT908"))
        if other_file1:
            named_files.append(("Additional Report 1", other_file1, "Unknown"))
        if other_file2:
            named_files.append(("Additional Report 2", other_file2, "Unknown"))

    # Configuration info
    with st.sidebar.expander("Configuration"):
        config_summary = config.get_config_summary()
        for key, value in config_summary.items():
            st.text(f"{key}: {value}")

    # Main content area
    all_files = []
    
    # Add multiple files from tab 1
    if uploaded_files:
        for i, file in enumerate(uploaded_files):
            all_files.append((f"Multiple Upload {i+1}: {file.name}", file, "Auto-detect"))
    
    # Add named files from tab 2
    all_files.extend(named_files)
    
    if all_files:
        st.header("Report Processing")
        
        # Show uploaded files summary
        st.info(f"📁 **{len(all_files)} file(s) ready for processing**")
        
        # Batch processing option
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("**Individual Processing:** Process each file separately below")
        with col2:
            if st.button("🚀 Process All Files", type="primary", use_container_width=True):
                st.session_state.batch_processing = True
                st.rerun()
        
        # Show batch processing results if enabled
        if hasattr(st.session_state, 'batch_processing') and st.session_state.batch_processing:
            st.success("🔄 **Batch Processing Mode Active** - Processing all files...")
            
            batch_results = []
            for i, (file_name, uploaded_file, expected_type) in enumerate(all_files):
                temp_path = f"temp_batch_{uploaded_file.name}_{i}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                try:
                    # Validate and process
                    validation_result = st.session_state.processor.validate_report(temp_path)
                    if validation_result["valid"]:
                        if uploaded_file.name.endswith(".csv"):
                            df = pd.read_csv(temp_path)
                        else:
                            df = pd.read_excel(temp_path)
                        
                        result = st.session_state.processor.execute_sop_workflow(
                            validation_result["report_type"], df
                        )
                        
                        batch_results.append({
                            "File": file_name,
                            "Type": validation_result["report_type"],
                            "Records": validation_result["row_count"],
                            "Status": "✅ Success" if result["success"] else "❌ Failed",
                            "Message": result.get("error", "Processed successfully")
                        })
                    else:
                        batch_results.append({
                            "File": file_name,
                            "Type": "Unknown",
                            "Records": 0,
                            "Status": "❌ Validation Failed",
                            "Message": validation_result["error"]
                        })
                except Exception as e:
                    batch_results.append({
                        "File": file_name,
                        "Type": "Error",
                        "Records": 0,
                        "Status": "❌ Error",
                        "Message": str(e)
                    })
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
            
            # Display batch results
            st.subheader("📊 Batch Processing Results")
            batch_df = pd.DataFrame(batch_results)
            st.dataframe(batch_df, use_container_width=True)
            
            # Summary statistics
            successful = len([r for r in batch_results if "✅" in r["Status"]])
            failed = len([r for r in batch_results if "❌" in r["Status"]])
            total_records = sum([r["Records"] for r in batch_results if isinstance(r["Records"], int)])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Successful", successful)
            with col2:
                st.metric("Failed", failed)
            with col3:
                st.metric("Total Records", f"{total_records:,}")
            
            # Reset batch processing
            if st.button("🔄 Process Again", use_container_width=True):
                st.session_state.batch_processing = False
                st.rerun()
        
        # Individual file processing
        if not (hasattr(st.session_state, 'batch_processing') and st.session_state.batch_processing):
            st.markdown("---")
            st.subheader("📋 Individual File Processing")
            
            # Process each file
            for i, (file_name, uploaded_file, expected_type) in enumerate(all_files):
                st.subheader(f"📄 {file_name}")
                
                # Show expected type if known
                if expected_type != "Unknown":
                    st.info(f"**Expected Type:** {expected_type}")
                
                # Save uploaded file temporarily
                temp_path = f"temp_{uploaded_file.name}_{i}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                try:
                    # Validate report
                    validation_result = st.session_state.processor.validate_report(temp_path)

                    if validation_result["valid"]:
                        st.success("✅ File validated successfully!")
                        st.info(f"**Detected Type:** {validation_result['report_type']}")
                        st.info(f"**Records:** {validation_result['row_count']:,}")
                        st.info(
                            f"**Columns:** {', '.join(validation_result['columns'][:10])}{'...' if len(validation_result['columns']) > 10 else ''}"
                        )
                        
                        # Show type comparison if expected type was specified
                        if expected_type != "Unknown" and expected_type != validation_result['report_type']:
                            st.warning(f"⚠️ **Type Mismatch:** Expected {expected_type}, but detected {validation_result['report_type']}")

                        # Process button for this specific file
                        if st.button(f"🚀 Process {file_name}", key=f"process_{i}", type="primary"):
                            with st.spinner(f"Processing {file_name}..."):
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
                                    st.success(f"✅ {file_name} processed successfully!")

                                    # Display summary
                                    st.subheader(f"Processing Summary - {file_name}")
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
                                    st.subheader(f"Data Preview - {file_name}")
                                    preview_df = pd.DataFrame(result["data"])
                                    st.dataframe(preview_df, use_container_width=True)

                                else:
                                    st.error(f"❌ Processing failed: {result['error']}")

                    else:
                        st.error(f"❌ File validation failed: {validation_result['error']}")
                        
                        # Show more details about why validation failed
                        if "Could not determine report type" in validation_result['error']:
                            st.warning("💡 **Tip:** Make sure your file has columns that indicate the report type:")
                            st.markdown("""
                            **For RPT600 (Payee Statement):**
                            - Look for columns like: `Payee`, `Commission`, `Dealer`, `Fee`
                            
                            **For RPT908 (Cancellation Report):**
                            - Look for columns like: `Cancellation_Reason`, `Contract`, `Refund_Amount`
                            """)
                            
                            # Show the actual columns in the file
                            try:
                                if uploaded_file.name.endswith(".csv"):
                                    df = pd.read_csv(temp_path)
                                else:
                                    df = pd.read_excel(temp_path)
                                
                                st.info(f"**Columns found in your file:** {', '.join(df.columns)}")
                            except:
                                pass

                except Exception as e:
                    st.error(f"❌ Error processing file: {str(e)}")
                    logger.error(f"Error in main: {str(e)}")

                finally:
                    # Clean up temp file
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                
                # Add separator between files
                if i < len(all_files) - 1:
                    st.markdown("---")

    else:
        st.info("👆 Please upload report files using the sidebar tabs above. You can use either multiple file upload or named uploads!")

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
