# OPEN FNR Process Artifacts

This directory stores executable process definitions for OPEN FNR Process Engine.

Sprint 0 contains only a development health-check process. Production processes
will be added incrementally by sprint:

- BPMN 2.0 for process flows.
- DMN for decision tables and business rules.
- CMMN for exception cases and collaborative work.

All process definitions must be versioned, reviewed, tested and traceable to
the corresponding business process specification.

Sprint 9 adds Process Engine foundation artifacts in `processes/process-engine`:

- `replenishment_approval_process.bpmn20.xml` for the first replenishment approval skeleton.
- `task_visibility_decision.dmn.xml` for role-based task visibility.
- `process_exception_case.cmmn.xml` for operational process exceptions.
