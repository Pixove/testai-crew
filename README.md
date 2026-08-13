# AI Test Case Generation with CrewAI

Scenario-driven test generation: a user writes a business scenario, and
CrewAI agents turn it into rules, business scenarios, test cases, test data,
pytest code, and a final coverage review for a SQLite database.

## Structure

```text
config/               Environment and project settings
data/                 Generated SQLite database and data generator
input/                User scenario description files
scripts/              Runnable command line tools
src/agents/           CrewAI agent definitions
src/tasks/            CrewAI task definitions
src/models/           Pydantic output models
src/crew/             Crew composition
src/database/         SQLite access helpers
src/llm/              LLM integration helpers
skills/               Agent skill definitions
tool/                 Custom CrewAI tools
business/             Local business rules and DB migrations (gitignored)
automated_tests/      Generated pytest tests (gitignored)
```

## Setup

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

## Inspect the database

```powershell
python scripts\inspect_database.py
python scripts\inspect_database.py --table products
python scripts\inspect_database.py --json
```

The database path comes from `DATABASE_PATH` in `.env` and defaults to
`data/campus_trade.db`.

## Quick start

```powershell
# 1. Put the scenario description into input/scenario.md
# 2. Run the full pipeline
python scripts\run_pipeline.py
# 3. Run the generated test file(s) shown in the pipeline output
python -m pytest automated_tests\test_orders.py -v
```

The full pipeline is the recommended entry point. `output/` and
`automated_tests/` are generated artifacts and are gitignored.

## Run scenario analyst

```powershell
python scripts\run_scenario_analyst.py
```

The scenario analyst reads `input/scenario.md` (or the path configured by
`SCENARIO_INPUT_PATH`), extracts structured business rules, and saves them to
`output/scenario_rules.json`.

## Generate schema JSON with descriptions

```powershell
python scripts\generate_schema_descriptions.py
python scripts\generate_schema_descriptions.py --table products
python scripts\generate_schema_descriptions.py --dry-run
```

The script reads the table structure, fetches 3 sample rows per table, asks the
model for a short Chinese description, and saves everything to
`output/schema_descriptions.json` by default.

## Run database analyst

```powershell
python scripts\run_database_analyst.py
```

The database analyst reads `scenario_rules.json`, checks the real database
schema, and generates only rule-related normal, boundary and exception
scenarios to `output/business_scenarios.json`.

## Run test case designer

```powershell
python scripts\run_test_case_designer.py
```

The test case designer reads the scenario rules and business scenarios, builds
a field combination matrix, and writes structured test cases to
`output/test_cases.json`.

## Run test data generator

```powershell
python scripts\run_test_data_generator.py
```

The test data generator reads the scenario rules and test cases, checks the
real schema, and writes concrete valid, invalid and boundary test data to
`output/test_data.json`.

## Run automation code generator

```powershell
python scripts\run_automation_code_generator.py
python -m pytest automated_tests -v
```

The code generator reads the scenario rules, test cases and test data, writes
executable pytest files under `automated_tests/`, and the generated suite is
saved to `output/generated_test_suite.json`. Use `--reuse` to regenerate the
files from the existing suite without calling the LLM.

## Run QA reviewer

```powershell
python scripts\run_qa_reviewer.py
```

The QA reviewer checks per-rule coverage, missing combinations and test data
consistency, then writes `output/coverage_report.json` and
`output/review_report.md`. Use `--reuse` to regenerate the reports from an
existing `coverage_report.json`.

Generated tests run against a local database that must contain the scenario
fields and triggers. Scenario-specific migrations live in `business/` and are
gitignored on purpose.

## Run full pipeline

```powershell
python scripts\run_pipeline.py
```

This runs all six agents in sequence, from `input/scenario.md` to
`output/review_report.md`, and writes the generated pytest files under
`automated_tests/`.

To run a different scenario file without overwriting the default input:

```powershell
python scripts\run_pipeline.py --scenario-file input\scenario_orders.md
```

Running the whole `automated_tests/` directory may include stale test files
from earlier scenarios. Use the specific test file paths printed by the
pipeline.
