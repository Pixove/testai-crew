---
name: test-data-generation
description: Guide the test data generator agent to create concrete, schema-consistent test data for every rule combination.
---

# test-data-generation

## Goals

Create concrete test data for every rule combination so the automated test
generator can execute the full combination matrix.

## Steps

1. Use the `read_scenario_rules` tool to read the field-dependency rules.
2. Use the `read_test_cases` tool to read the test cases file.
3. Use the `inspect_database` tool to confirm real table names, field names and
   field types.
4. Generate at least one data record for every test case and every meaningful
   combination from the rules.
5. Cover valid, invalid and boundary data explicitly:
   - `valid`: data that should be accepted.
   - `invalid`: data that should be rejected or exposes a defect.
   - `boundary`: edge values such as 0, negative, empty, maximum and minimum.
6. Respect primary key uniqueness, non-null fields and foreign key references.
   If the schema has no constraint, record that in `expected_result`.
7. Fill `rule_id` with the source rule id for traceability.
8. Output the records as `TestDataDocument` JSON.
