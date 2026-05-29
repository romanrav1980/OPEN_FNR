from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MAIN = ROOT / "apps" / "frontend" / "src" / "main.tsx"


def _main_text() -> str:
    return MAIN.read_text(encoding="utf-8")


def test_integration_and_dq_sections_are_present() -> None:
    text = _main_text()

    for marker in (
        "Shadow Load Gate",
        "Data Quality Console",
        "Integration Operations Console",
        "Daily Pipeline Gate",
        "Source readiness, retry plan, reconciliation and downstream blockers",
    ):
        assert marker in text


def test_integration_operations_api_contracts_are_wired_through_shared_config() -> None:
    text = _main_text()

    for endpoint in (
        "/integration/operations/source-readiness",
        "/integration/operations/retry-plan",
        "/integration/operations/reconciliation",
    ):
        assert endpoint in text

    assert "apiUrl(" in text
    assert "http://localhost" not in text
    assert "127.0.0.1" not in text


def test_integration_ui_exposes_retry_reconciliation_and_audit_context() -> None:
    text = _main_text()

    for marker in (
        "Idempotency key",
        "same_idempotency_key_no_duplicate_clean_rows",
        "Downstream blockers",
        "Every recovery action is traceable",
        "linked Process Engine task",
        "Request resend",
        "Run retry",
        "Open reconciliation",
    ):
        assert marker in text


def test_data_quality_ui_exposes_blocker_and_waiver_context() -> None:
    text = _main_text()

    for marker in (
        "Blocking incidents, waivers and re-checks",
        "Waiver requires Data Owner or Admin",
        "Blocking DQ incidents stop publication",
        "Re-run",
        "Waive",
        "Export rows",
    ):
        assert marker in text


def test_integration_and_dq_sections_are_accessibly_labeled() -> None:
    text = _main_text()

    for aria_label in (
        'aria-label="Shadow load gate"',
        'aria-label="Data quality console"',
        'aria-label="Integration operations console"',
        'aria-label="Daily pipeline gate"',
    ):
        assert aria_label in text
