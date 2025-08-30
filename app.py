"""
Main entry point for Cancellations SOP Processor
This is a new file to force Streamlit Cloud to update
"""

import streamlit as st

# Redirect to the main app
st.set_page_config(page_title="Cancellations SOP Processor", page_icon="📊")

st.title("🔄 **Updating Application...**")
st.info("Please wait while the application updates with new features.")

# Import and run the main app
try:
    # Import the main application
    from streamlit_app import main
    main()
except Exception as e:
    st.error(f"Error loading application: {str(e)}")
    st.info("Please check the deployment logs in Streamlit Cloud.")
