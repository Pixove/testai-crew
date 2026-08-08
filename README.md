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
src/database/         SQLite access helpers
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
