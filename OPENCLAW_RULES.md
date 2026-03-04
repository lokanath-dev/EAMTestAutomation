# OpenClaw Rules for EAMTestAutomation

## Priorities
1) Working end-to-end single-test run from Streamlit UI
2) Stability > features
3) Keep everything local; no CI required

## Architecture
- Streamlit UI only (single app entry: app.py)
- Runner executes exactly one selected test case + one selected dataset
- Actions are hardcoded Python classes/functions, surfaced in UI as human-readable names
- Page Object Model for locators and UI interactions
- GraphQL client supports simple POST to configured endpoint; no auth

## Conventions
- Python >= 3.12
- Use pathlib, dataclasses, typing
- Keep modules small; no circular imports
- Use Playwright get_by_role/get_by_label first; avoid xpath

## Results
- Create temp run dir per run (e.g., .tmp/runs/<timestamp>/)
- Store logs, trace.zip, screenshot.png on failure
- Delete temp run dir after run unless user exports PDF
