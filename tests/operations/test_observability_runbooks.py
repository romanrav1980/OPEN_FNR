from pathlib import Path


STRATEGY = Path("OBSERVABILITY_RUNBOOKS_STRATEGY.md")
PUBLICATION_RUNBOOK = Path("docs/runbooks/publication-export-failure.md")


def test_observability_strategy_defines_slo_alert_trace_and_runbook_contracts() -> None:
    text = STRATEGY.read_text(encoding="utf-8")

    assert "GET /observability/slo-targets" in text
    assert "GET /observability/alert-rules" in text
    assert "GET /observability/trace-propagation" in text
    assert "GET /observability/runbook-drills" in text
    assert "No alert rule may depend on a hardcoded host, IP address, port or external dashboard URL." in text


def test_publication_export_failure_runbook_contains_recovery_drill_steps() -> None:
    text = PUBLICATION_RUNBOOK.read_text(encoding="utf-8")

    assert "Annotation" in text
    assert "Step-by-Step Recovery" in text
    assert "idempotency key" in text
    assert "duplicate-publication guard result" in text
    assert "Escalation" in text
