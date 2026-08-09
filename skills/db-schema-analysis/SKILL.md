---
name: db-schema-analysis
description: Guide the database analyst agent to interpret arbitrary database schemas and extract normal, boundary and exception business scenarios.
---

# db-schema-analysis

## Goals

Analyze an arbitrary SQLite database and produce structured business scenarios.

## Steps

1. Use the `inspect_database` tool to read all tables, columns, row counts,
   indexes and foreign keys.
2. For every table, infer the business meaning of the fields from names, types,
   constraints and sample values.
3. Create scenarios in three categories:
   - `normal`: happy path flows for the table.
   - `boundary`: edge values such as empty, zero, maximum, minimum and status
     transitions.
   - `exception`: invalid inputs, missing required data, broken references and
     illegal states.
4. Keep scenario descriptions concise and grounded in the actual schema; do not
   invent tables or fields that do not exist.
5. Output the scenarios as `BusinessScenarioDocument` JSON.
