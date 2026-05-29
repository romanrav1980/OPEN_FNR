from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MAIN = ROOT / "apps" / "frontend" / "src" / "main.tsx"


def _main_text() -> str:
    return MAIN.read_text(encoding="utf-8")


def test_admin_and_process_sections_are_present() -> None:
    text = _main_text()

    for marker in (
        "Admin Console V1",
        "Process Engine Task Inbox",
        "Process Deployment",
        "Flowable Upload Gate",
        "BPMN Quality",
    ):
        assert marker in text


def test_security_admin_api_contracts_are_wired_through_shared_config() -> None:
    text = _main_text()

    for endpoint in (
        "/security/users?actor_role=Admin",
        "/security/access-requests?actor_role=Security%20Owner",
        "/security/service-accounts?actor_role=Admin",
        "/security/access-review/report?business_date=2026-05-29&actor_role=Security%20Owner",
        "/security/policy-check?user_id=u-viewer-001&region=north&category=fresh&allowed_role=Viewer",
    ):
        assert endpoint in text

    assert "apiUrl(" in text
    assert "http://localhost" not in text
    assert "127.0.0.1" not in text


def test_admin_ui_exposes_rbac_service_account_and_access_review_context() -> None:
    text = _main_text()

    for marker in (
        "Viewer cannot open Admin users",
        "Service account",
        "Secret rotation",
        "Access Review",
        "Security Owner reviews privileged, inactive and excessive access",
        "Role, service account and object-scope decisions use shared backend policy helpers",
    ):
        assert marker in text

    assert "secret value" not in text.lower()


def test_process_operations_ui_exposes_task_actions_audit_and_quality_gates() -> None:
    text = _main_text()

    for marker in (
        "BPMN / DMN / CMMN tasks, actions and audit trail",
        "Human task must have role, SLA and audit expectations confirmed",
        "Deployability Gate",
        "Runtime Strategy",
        "gateway alternatives, dead-end paths and cognitive challenges",
    ):
        assert marker in text


def test_admin_and_process_sections_are_accessibly_labeled() -> None:
    text = _main_text()

    for aria_label in (
        'aria-label="Admin Console"',
        'aria-label="Process engine task inbox"',
        'aria-label="Promo approval process"',
    ):
        assert aria_label in text
