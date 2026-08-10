---
name: test-case-design
description: Guide the test case designer agent to turn business scenarios and rules into complete combination-matrix test cases.
---

# test-case-design

## Goals

Turn business scenarios and field-dependency rules into complete test cases
that cover every meaningful combination.

## Steps

1. Use the `read_scenario_rules` tool to read the field-dependency rules.
2. Use the `read_business_scenarios` tool to read the scenario context.
3. Use the `inspect_database` tool to confirm real field names and types.
4. Build a combination matrix for every dependency, for example:
   - trigger value allowed and affected value allowed
   - trigger value allowed and affected value forbidden
   - trigger value at a boundary
   - NULL values when the scenario does not define them
5. Generate at least one test case per meaningful combination. Keep the
   `normal`, `boundary` or `exception` category.
6. Every test case must include:
   - `id`, `title` and the target `table`
   - the source `scenario_id`
   - the source `rule_id`
   - `preconditions` that make the test state clear
   - concrete `steps` in execution order
   - `test_data` values that match the table field types
   - a verifiable `expected_result`
7. Use real field names and values from the schema; avoid vague placeholders.
8. Output the cases as `TestCaseDocument` JSON.
