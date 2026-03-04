"""Dataset manager UI."""

from pathlib import Path
import streamlit as st

from src.eam_automation.models.dataset import Dataset
from src.eam_automation.storage.yaml_store import save_dataset


def render_dataset_manager(repo_root: Path) -> None:
    st.title("Dataset Manager")

    dataset_name = st.text_input("Dataset Name")
    member_id = st.text_input("Member ID")
    scenario = st.text_input("Scenario")

    if st.button("Save Dataset"):
        dataset = Dataset(
            name=dataset_name,
            fields={
                "member_id": member_id,
                "scenario": scenario,
            },
        )
        save_dataset(repo_root, dataset)
        st.success(f"Saved dataset: {dataset_name}")
