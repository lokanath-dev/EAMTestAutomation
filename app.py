"""Streamlit entrypoint for the EAM Test Automation Tool."""

import sys
import asyncio
from pathlib import Path

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import streamlit as st

from src.eam_automation.config.loader import load_environments
from src.eam_automation.ui.dashboard import render_dashboard
from src.eam_automation.ui.test_case_builder import render_test_case_builder
from src.eam_automation.ui.dataset_manager import render_dataset_manager
from src.eam_automation.ui.test_runner import render_test_runner


st.set_page_config(page_title="EAM Test Automation", layout="wide")


def _ensure_state() -> None:
    if "selected_view" not in st.session_state:
        st.session_state.selected_view = "Dashboard"


def _sidebar(env_path: Path) -> None:
    st.sidebar.title("EAM Tool")
    environments = load_environments(env_path)
    env_names = list(environments.keys())
    default = 0 if env_names else None

    if env_names:
        selected_env = st.sidebar.selectbox("Environment", env_names, index=default)
        st.session_state["selected_env"] = selected_env
    else:
        st.sidebar.warning("No environments configured.")

    st.session_state.selected_view = st.sidebar.radio(
        "Navigate",
        ["Dashboard", "Test Case Builder", "Dataset Manager", "Test Runner"],
        index=["Dashboard", "Test Case Builder", "Dataset Manager", "Test Runner"].index(
            st.session_state.selected_view
        ),
    )


def main() -> None:
    _ensure_state()
    repo_root = Path(__file__).resolve().parent
    env_path = repo_root / "config" / "environments.yaml"

    _sidebar(env_path)

    view = st.session_state.selected_view
    if view == "Dashboard":
        render_dashboard()
    elif view == "Test Case Builder":
        render_test_case_builder(repo_root)
    elif view == "Dataset Manager":
        render_dataset_manager(repo_root)
    elif view == "Test Runner":
        render_test_runner(repo_root)


if __name__ == "__main__":
    main()
