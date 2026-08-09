# AI Test Case Generation with CrewAI

Project skeleton for generating AI-powered automation test cases from a
campus second-hand trading SQLite database using multiple CrewAI agents.

## Structure

```text
config/               Environment and project settings
data/                 Generated SQLite database and data generator
scripts/              Runnable command line tools
src/agents/           CrewAI agent definitions
src/tasks/            CrewAI task definitions
src/models/           Pydantic output models
src/crew/             Crew composition
src/database/         SQLite access helpers
src/llm/              LLM integration helpers
skills/               Agent skill definitions
tool/                 Custom CrewAI tools
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

The database analyst reads the database schema, extracts normal, boundary and
exception business scenarios, and saves them to
`output/business_scenarios.json`.

## Run test case designer

```powershell
python scripts\run_test_case_designer.py
```

The test case designer reads `output/business_scenarios.json` and writes
structured test cases to `output/test_cases.json`.

## Run test data generator

```powershell
python scripts\run_test_data_generator.py
```

The test data generator reads `output/test_cases.json`, checks the real schema,
and writes concrete valid, invalid and boundary test data to
`output/test_data.json`.
