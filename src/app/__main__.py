"""
Entry point for running the Streamlit application
"""

import os
import sys

import streamlit.web.cli as stcli


def main():
    """Run the Streamlit application"""
    # Add the src directory to Python path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

    # Run Streamlit
    sys.argv = [
        "streamlit",
        "run",
        "src/app/main.py",
        "--server.port=8501",
        "--server.address=0.0.0.0",
    ]
    sys.exit(stcli.main())


if __name__ == "__main__":
    main()
