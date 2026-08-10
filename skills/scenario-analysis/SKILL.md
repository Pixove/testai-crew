---
name: scenario-analysis
description: Guide the scenario analyst agent to convert user scenario descriptions into structured business rules.
---

# scenario-analysis

## Goals

Convert a user-provided scenario description into structured business rules
that later agents can use to generate test cases.

## Steps

1. Use the `read_scenario_file` tool to read the user scenario file.
2. Identify the target tables and fields mentioned in the scenario.
3. Extract explicit conditions and field dependencies, such as:
   - when field A equals a value, field B must be a specific value
   - when field A is above a threshold, field B may or may not be allowed
4. Record allowed values, forbidden values, NULL behavior and boundary notes.
5. Do not invent rules that are not present in the scenario file.
6. Output the result as `ScenarioRulesDocument` JSON.
