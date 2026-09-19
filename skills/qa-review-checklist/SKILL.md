---
name: qa-review-checklist
description: Guide the QA reviewer agent to check test coverage and evaluate the final effect of the generated test suite.
---

# qa-review-checklist

## Goals

Check whether every rule and every meaningful combination is covered, and
produce a final quality evaluation.

## Steps

1. Use `read_scenario_rules`, `read_business_scenarios`, `read_test_cases` and
   `read_test_data` to read all generated artifacts.
2. Use `read_pytest_result` to read the real pytest execution result, including
   pass/fail counts and failure messages such as `规则未落地` or `字段未落地`.
3. For every rule, count linked scenarios, test cases and data records.
4. Check the combination matrix:
   - allowed values
   - forbidden values
   - boundary values
   - NULL behavior
5. List every combination that is missing or only partially covered.
6. Provide a provisional `quality_score`; the pipeline replaces it with a
   deterministic score computed from coverage and execution results.
7. Output `ReviewReport` JSON with recommendations and a final conclusion.
