"""Test case builder UI."""

from pathlib import Path
import streamlit as st

from src.eam_automation.actions.library import ACTION_REGISTRY
from src.eam_automation.models.test_case import TestCase, TestStep
from src.eam_automation.storage.yaml_store import save_test_case


def render_test_case_builder(repo_root: Path) -> None:
    st.title("Test Case Builder")

    name = st.text_input("Test Case Name")
    description = st.text_area("Description")
    tags = st.text_input("Tags (comma-separated)")

    st.subheader("Step")
    action_name = st.selectbox("Action", list(ACTION_REGISTRY.keys()))
    params_raw = st.text_area("Parameters (key=value per line)")

    if st.button("Save Test Case"):
        params = {}
        for line in params_raw.splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                params[k.strip()] = v.strip()

        step = TestStep(action=action_name, params=params)
        tc = TestCase(
            name=name,
            description=description,
            tags=[t.strip() for t in tags.split(",") if t.strip()],
            steps=[step],
            datasets=[],
        )
        save_test_case(repo_root, tc)
        st.success(f"Saved test case: {name}")
