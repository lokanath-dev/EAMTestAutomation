"""Test runner UI."""

from pathlib import Path
import streamlit as st

from src.eam_automation.runner.playwright_runner import run_test_case
from src.eam_automation.storage.yaml_store import list_datasets, list_test_cases
from src.eam_automation.reporting.pdf_exporter import export_pdf_report


def render_test_runner(repo_root: Path) -> None:
    st.title("Test Runner")

    test_cases = list_test_cases(repo_root)
    datasets = list_datasets(repo_root)

    if not test_cases or not datasets:
        st.info("Create at least one test case and one dataset first.")
        return

    tc_name = st.selectbox("Test Case", test_cases)
    ds_name = st.selectbox("Dataset", datasets)

    if st.button("Run"):
        result = run_test_case(repo_root, tc_name, ds_name)
        st.json(result)
        st.session_state["last_result"] = result

    if st.button("Export Last Result to PDF") and st.session_state.get("last_result"):
        out_path = export_pdf_report(repo_root, st.session_state["last_result"])
        st.success(f"PDF exported: {out_path}")
