---
name: pytest-automation
description: Guide the automation code generator agent to turn test cases and test data into executable pytest files for SQLite.
---

# pytest-automation

## Goals

Generate executable pytest files that run against a temporary copy of the
database and verify whether the data behavior matches the scenario rules.

## Steps

1. Use the `read_scenario_rules`, `read_test_cases` and `read_test_data` tools
   to read the generated inputs.
2. Use the `inspect_database` tool to confirm real table and field names.
3. Generate `conftest.py` with a fixture that reads the source database path
   using `from config.settings import get_settings` and
   `get_settings().database_path`. Do not use `config.settings.DATABASE_PATH`.
   Copy the database into a temporary file and enable foreign keys. Do not scan
   directories with glob. Never modify the source database.
4. Generate one test file per table, for example `test_products.py`.
5. Name every test function after its test case id, for example
   `test_tc_products_001`.
6. Before running SQL, check that every field used by the test data exists in
   the table. If a field is missing, fail with a clear `字段未落地` message.
7. Execute the operation from the test data record, then assert the expected
   result. If the rule says the data should be rejected but the database
   accepts it, fail with `规则未落地`.
8. When the expected result says the behavior is undefined or pending business
   confirmation, the test should accept either a clean rejection or an explicit
   inserted value; do not blindly assert insertion success.
9. Output the generated files as `GeneratedTestSuite` JSON.
