---
name: test-data-generation
description: Guide the test data generator agent to create concrete, schema-consistent test data for every test case.
---

# test-data-generation

## Goals

Create concrete test data that can be used by the automated test generator.

## Steps

1. Use the `read_test_cases` tool to read the test cases file.
2. Use the `inspect_database` tool to confirm real table names, field names and
   field types.
3. Generate at least one data record for every test case.
4. Cover valid, invalid and boundary data explicitly:
   - `valid`: data that should be accepted.
   - `invalid`: data that should be rejected or exposes a defect.
   - `boundary`: edge values such as 0, negative, empty, maximum and minimum.
5. Respect primary key uniqueness, non-null fields and foreign key references.
   If the schema has no constraint, record that in `expected_result`.
6. Output the records as `TestDataDocument` JSON.
