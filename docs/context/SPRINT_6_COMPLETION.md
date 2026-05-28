# Sprint 6 Completion Snapshot

Date: 2026-05-28

## Scope Completed

Sprint 6 implemented ML Regular Model V1 foundation:

- model version metadata contract;
- baseline vs ML candidate comparison;
- WAPE delta, Bias delta and fallback availability;
- model approval role gate;
- `/ml-models/versions` API;
- `/ml-models/versions/{model_version}` API;
- `/ml-models/versions/{model_version}/comparison` API;
- BPMN `model_candidate_review_process`;
- DMN `model_approval_decision`;
- CMMN `model_degradation_case`;
- UI Model Monitoring V1;
- HTML UI/process test report with screenshot.

## Business Process Focus

The model lifecycle now has an explicit path:

1. Model is registered as a candidate.
2. Backtesting runs and records metrics.
3. DMN checks whether the candidate improves WAPE, keeps Bias within threshold and has fallback.
4. Forecast Owner or ML Owner approves or rejects the candidate.
5. Approved model can be promoted.
6. If degradation is detected, CMMN case manages investigation, baseline fallback and retraining.

## UI Focus

The UI now shows:

- ML candidate model card;
- approval gate;
- baseline comparison;
- WAPE/Bias values;
- model delta;
- fallback model;
- Approve, Reject and Activate fallback actions.

## Verification Results

```text
python -m pytest
51 passed

npm.cmd run build
vite build completed

Playwright screenshot
model-monitoring-v1.png saved
```

## Test Report

`docs/test-reports/sprint-6-ml-regular-model/index.html`

## Known Notes

- Sprint 6 implements ML metadata, governance and comparison contracts.
- Physical training/inference and MLflow integration are not yet implemented.
- UI is static and will be connected to API in a later frontend integration slice.

## Next Sprint

Sprint 7 should continue the ML/forecasting block with backtesting and monitoring:

- rolling backtesting contract;
- model drift and degradation indicators;
- model monitoring API;
- monitoring UI;
- process for model degradation and retraining escalation;
- HTML report and screenshot.
