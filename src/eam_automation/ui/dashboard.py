"""Dashboard view."""

import streamlit as st


def render_dashboard() -> None:
    st.title("EAM Test Automation Dashboard")
    st.markdown(
        """
        Use the sidebar to:
        - Create/Edit test cases
        - Manage datasets
        - Run one test case + one dataset sequentially
        - Export run results to PDF
        """
    )
