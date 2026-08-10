---
name: db-schema-analysis
description: Guide the database analyst agent to analyze only the tables and fields involved in the user scenario rules and produce scenario-focused business scenarios.
---

# db-schema-analysis

## Goals

Analyze the database structures relevant to `scenario_rules.json` and produce
business scenarios for every user-defined rule.

## Steps

1. Use the `read_scenario_rules` tool to read the user rules.
2. Use the `inspect_database` tool to read the real table, column, foreign key
   and row count information.
3. Optionally use the `read_schema_json` tool to get field business meanings and
   sample rows.
4. Analyze only the tables and fields mentioned in the rules. Do not generate
   scenarios for unrelated tables.
5. For every rule, create scenarios in three categories:
   - `normal`: rule-compliant behavior.
   - `boundary`: edge values such as zero, negative, empty and NULL.
   - `exception`: rule violations and invalid combinations.
6. Fill `rule_id` with the source rule id and `fields` with the fields involved.
7. Output the scenarios as `BusinessScenarioDocument` JSON.
