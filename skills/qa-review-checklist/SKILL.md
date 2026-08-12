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
2. For every rule, count linked scenarios, test cases and data records.
3. Check the combination matrix:
   - allowed values
   - forbidden values
   - boundary values
   - NULL behavior
4. List every combination that is missing or only partially covered.
5. Score the suite from 0 to 100 based on coverage completeness and consistency.
6. Output `ReviewReport` JSON with recommendations and a final conclusion.
