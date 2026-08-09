---
name: test-case-design
description: Guide the test case designer agent to turn business scenarios into complete, concrete and executable test cases.
---

# test-case-design

## Goals

Turn business scenarios into complete test cases that can be executed by
automated tests.

## Steps

1. Use the `read_business_scenarios` tool to read the business scenarios file.
2. Design at least one test case for each scenario. Keep the original
   `normal`, `boundary` or `exception` category.
3. Every test case must include:
   - `id`, `title` and the target `table`
   - the source `scenario_id`
   - `preconditions` that make the test state clear
   - concrete `steps` in execution order
   - `test_data` values that match the table field types
   - a verifiable `expected_result`
4. Use real field names and values from the schema; avoid vague placeholders.
5. Output the cases as `TestCaseDocument` JSON.
