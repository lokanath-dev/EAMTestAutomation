"""Test case builder UI with ordered multi-step support."""

from __future__ import annotations

from pathlib import Path
import json
import streamlit as st

from src.eam_automation.actions.library import ACTION_REGISTRY
from src.eam_automation.models.test_case import TestCase, TestStep
from src.eam_automation.storage.yaml_store import list_test_cases, load_test_case, save_test_case


def _parse_params(params_raw: str) -> dict:
    """Parse JSON first; fallback to key=value lines."""
    raw = params_raw.strip()
    if not raw:
        return {}

    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass

    params: dict[str, str] = {}
    for line in raw.splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            params[k.strip()] = v.strip()
    return params


def _ensure_builder_state() -> None:
    st.session_state.setdefault("tc_steps", [])
    st.session_state.setdefault("tc_loaded_name", "")


def _steps_table(steps: list[dict]) -> None:
    if not steps:
        st.info("No steps yet.")
        return

    rows = []
    for idx, step in enumerate(steps, start=1):
        rows.append(
            {
                "order": idx,
                "step_name": step.get("step_name", ""),
                "action_name": step.get("action_name", ""),
                "parameters": json.dumps(step.get("parameters", {})),
            }
        )
    st.dataframe(rows, use_container_width=True, hide_index=True)


def render_test_case_builder(repo_root: Path) -> None:
    st.title("Test Case Builder")
    _ensure_builder_state()

    existing = list_test_cases(repo_root)
    selected_existing = st.selectbox("Select Test Case", ["<new>"] + existing)

    if selected_existing != "<new>" and selected_existing != st.session_state.get("tc_loaded_name"):
        loaded = load_test_case(repo_root, selected_existing)
        st.session_state.tc_loaded_name = selected_existing
        st.session_state.tc_steps = loaded.get("steps", [])
        st.session_state.tc_desc = loaded.get("description", "")
        st.session_state.tc_tags = ", ".join(loaded.get("tags", []))

    if selected_existing == "<new>" and st.session_state.get("tc_loaded_name") != "":
        st.session_state.tc_loaded_name = ""
        st.session_state.tc_steps = []
        st.session_state.tc_desc = ""
        st.session_state.tc_tags = ""

    default_name = selected_existing if selected_existing != "<new>" else ""
    name = st.text_input("Test Case Name", value=default_name)
    description = st.text_area("Description", value=st.session_state.get("tc_desc", ""))
    tags = st.text_input("Tags (comma-separated)", value=st.session_state.get("tc_tags", ""))
    file_type = st.selectbox("File format", [".yaml", ".json"], index=0)

    st.subheader("Ordered Steps")
    _steps_table(st.session_state.tc_steps)

    st.markdown("### Step Editor")
    step_count = len(st.session_state.tc_steps)
    selected_idx = st.number_input(
        "Step index (1-based) for Edit/Delete/Move",
        min_value=1,
        max_value=max(1, step_count),
        value=1,
        step=1,
    )

    action_names = list(ACTION_REGISTRY.keys())
    step_name = st.text_input("step_name")
    action_name = st.selectbox("action_name", action_names)
    params_raw = st.text_area("parameters (JSON object or key=value per line)", value="{}")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if st.button("Add Step"):
            step = {
                "step_name": step_name or action_name,
                "action_name": action_name,
                "parameters": _parse_params(params_raw),
            }
            st.session_state.tc_steps.append(step)
            st.success("Step added.")

    with col2:
        if st.button("Edit Step"):
            if step_count == 0:
                st.warning("No step to edit.")
            else:
                i = int(selected_idx) - 1
                st.session_state.tc_steps[i] = {
                    "step_name": step_name or action_name,
                    "action_name": action_name,
                    "parameters": _parse_params(params_raw),
                }
                st.success(f"Step {selected_idx} updated.")

    with col3:
        if st.button("Delete Step"):
            if step_count == 0:
                st.warning("No step to delete.")
            else:
                i = int(selected_idx) - 1
                st.session_state.tc_steps.pop(i)
                st.success(f"Step {selected_idx} deleted.")

    with col4:
        if st.button("Move Up"):
            i = int(selected_idx) - 1
            if i > 0 and step_count > 1:
                st.session_state.tc_steps[i - 1], st.session_state.tc_steps[i] = (
                    st.session_state.tc_steps[i],
                    st.session_state.tc_steps[i - 1],
                )
                st.success("Step moved up.")

    with col5:
        if st.button("Move Down"):
            i = int(selected_idx) - 1
            if 0 <= i < step_count - 1:
                st.session_state.tc_steps[i + 1], st.session_state.tc_steps[i] = (
                    st.session_state.tc_steps[i],
                    st.session_state.tc_steps[i + 1],
                )
                st.success("Step moved down.")

    if st.button("Save Test Case"):
        if not name.strip():
            st.error("Test case name is required.")
            return

        steps = [TestStep(**s) for s in st.session_state.tc_steps]
        tc = TestCase(
            name=name.strip(),
            description=description,
            tags=[t.strip() for t in tags.split(",") if t.strip()],
            steps=steps,
            datasets=[],
        )
        save_test_case(repo_root, tc, ext=file_type)
        st.session_state.tc_loaded_name = name.strip()
        st.success(f"Saved test case: {name}{file_type}")
