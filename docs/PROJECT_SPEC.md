# EAM Test Automation Tool — Specification

## 1. Product Overview
- Application: Enrollment Application Manager (EAM)
- Vendor: TriZetto Elements
- Organization: Blue Cross NC (licensed user)
- Audience: internal admins only
- Access: Web UI, VPN required
- Browser: Google Chrome (Chromium via Playwright)

Primary admin goals:
- View enrollment applications
- Fix fallouts
- Validate eligibility with CMS (via BEQ / TRR concepts)
- Simulate batch inputs by generating and uploading test files

Out of scope:
- Production execution (never run in Prod)
- Running batch jobs via automation (no scheduling/executing batch jobs)

## 2. Execution Model
- Local machine only
- Run only ONE selected test case + ONE selected dataset
- Sequential only (no parallelization)
- Each run uses a new Playwright browser session (isolation)

## 3. Tech Stack
- Python: >=3.12
- UI: Streamlit (single app)
- Browser automation: Playwright (Python)
- Test framework: Pytest (used internally by runner or directly invoked)
- Locators: Playwright accessible selectors (get_by_role/get_by_label/get_by_text)

## 4. Environments & Configuration
Multiple non-prod environments: DEV1, DEV2, UAT, TEST (etc).
No Prod.

Configuration must be externalized (URLs configured later):
- Base UI URL per environment
- GraphQL endpoint per environment

## 5. GraphQL Backend Validation
- GraphQL APIs exist that fetch data from DB
- Internal network only; no auth required
- Endpoint varies by environment and is configured

Validation queries may require multiple fields (not fixed yet).
Framework must support configurable query params per validation step.

## 6. Test Case Builder UI (Tester-facing)
Single app:
- Run: `streamlit run app.py`
- Access: http://localhost:8501

Home: Dashboard (navigation)
- Create/Edit Test Case
- Manage Datasets
- Run Test
- Import Templates (later)
- Export Run Result to PDF (on demand)

### Save behavior
- Save test cases/steps/data locally into the git repo folder (human-readable)
- No git operations automated (tester commits manually)

### Results behavior
- Do NOT persist results by default
- During run create temporary artifacts:
  - screenshot on failure
  - execution logs
  - Playwright trace
- Temporary artifacts are deleted after run or app exit unless user exports PDF
- Export to PDF should include step outcomes + logs + embedded screenshots (if any)

## 7. Test Case Model
Each Test Case:
- name, description, tags
- ordered steps
- multiple datasets supported (Option B)
Run: choose one dataset at a time.

## 8. Steps as Reusable Human-Readable Actions
Steps are built from an action library:
- Actions are hardcoded in Python (not user-defined)
- UI shows actions in plain English (no abbreviations)
- Each step selects an action + provides parameters

Examples (illustrative):
- Open Enrollment Application Manager
- Generate Enrollment Application File
- Generate BQN Response File
- Generate TRR File
- Upload Enrollment Application File
- Upload BQN Response File
- Upload TRR File
- Verify Processing Status Is
- Wait Until Processing Completes
- Search Application By Member ID
- Open Application Details
- Verify Application Status Is
- Fix Application Fallout
- Validate Backend State via GraphQL

## 9. File Generation & Upload
The tool must generate CMS-like input files for test scenarios:
- EAF
- BQN response
- TRR

Approach: HYBRID generator
- Base templates exist and will be committed later under templates/
- Tester provides scenario fields in dataset
- Tool generates valid files per template + dataset fields
- Upload occurs via EAM UI (single upload step)

EAM shows immediate processing status in UI.

## 10. Maintainability Patterns
Use Page Object Model:
- Pages contain locators and UI interactions
- Actions call pages
- Runner orchestrates actions for a test case

## 11. Debugging via Jupyter
Jupyter notebooks are supported for debugging Python modules (generators, graphql client, sqlite/data model),
but Playwright UI runs through the Streamlit app/runner.
