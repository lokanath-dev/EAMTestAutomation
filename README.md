# EAM Test Automation Tool

Scaffolded Python project for Blue Cross NC internal EAM non-prod test automation.

## Tech
- Python 3.12+
- Streamlit UI
- Playwright runner
- YAML test cases/datasets
- SQLite metadata DB
- GraphQL client
- PDF export

## Run
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium
streamlit run app.py
```

## Structure
- `app.py` - Streamlit app entrypoint
- `src/eam_automation/ui` - Dashboard, Test Case Builder, Dataset Manager, Test Runner
- `src/eam_automation/runner` - Playwright orchestration
- `src/eam_automation/pages` - Page Object Model classes
- `src/eam_automation/actions` - reusable action library
- `src/eam_automation/storage` - YAML read/write helpers
- `src/eam_automation/db` - SQLite metadata helper
- `src/eam_automation/generators` - EAF/BQN/TRR generators
- `src/eam_automation/graphql` - GraphQL client
- `src/eam_automation/artifacts` - temp artifacts management
- `src/eam_automation/reporting` - PDF report export
- `config/environments.yaml` - environment config
- `storage/test_cases`, `storage/datasets` - human-readable test assets
- `tmp/screenshots`, `tmp/logs`, `tmp/traces` - ephemeral artifacts

## Notes
- Execution model: one test case + one dataset at a time, sequentially.
- No production usage.
- URLs/endpoints in `config/environments.yaml` are placeholders.
