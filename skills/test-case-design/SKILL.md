---
name: test-case-design
description: Guide the test case designer agent to turn business scenarios and rules into complete combination-matrix test cases.
---

# test-case-design

## Goals

Turn business scenarios and field-dependency rules into complete test cases
that cover every meaningful combination.

## Steps

1. Use the `build_pairwise_matrix` tool to get the minimized pairwise
   combination matrix.
2. Use `read_scenario_rules`, `read_business_scenarios` and `inspect_database`
   to add rule, scenario and schema context.
3. Generate one test case per pairwise combination. Do not expand the matrix
   into a full cartesian product.
4. For rules without structured dependencies, add boundary and exception cases
   based on the business description.
5. Keep the
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
