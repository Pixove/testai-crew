# Orders Rule Scenario Sample

This sample demonstrates the scenario-driven pipeline with the `orders` table.

## Contents

- `sample.db` - local database with orders rule triggers applied
- `scenario.md` - user scenario description
- `scenario_rules.json` - extracted business rules
- `business_scenarios.json` - rule-related business scenarios
- `test_cases.json` - generated test cases
- `test_data.json` - generated test data
- `generated_test_suite.json` - generated pytest suite
- `coverage_report.json` - QA coverage report
- `review_report.md` - QA review report
- `automated_tests/` - executable pytest files

## Rules

- `deal_price` must be greater than 0
- when status is `已完成`, `completed_at` must not be empty
- when status is `已取消`, `completed_at` must be empty
- `buyer_id` cannot equal `seller_id`
- `status` can only be one of: `待付款`, `待发货`, `待收货`, `已完成`, `已取消`

## Expected failures

The `status` enum rule is intentionally NOT implemented in the sample
database. Running the sample tests will report 5 expected failures with
`规则未落地: status=...` messages. This demonstrates that the generated tests
can detect rules that exist in the scenario but are not enforced by the
database.

To make these tests pass, add a `CHECK` constraint or trigger that only allows
the five status values.

## Run the sample tests

```powershell
python -m pytest samples\orders-rule-scenario\automated_tests -v
```

The sample conftest reads `sample.db` from the same directory, so no extra
database setup is needed.
