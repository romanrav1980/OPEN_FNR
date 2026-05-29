from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CI = ROOT / ".github" / "workflows" / "ci.yml"
RELEASE_TEMPLATE = ROOT / "docs" / "release" / "RELEASE_NOTES_TEMPLATE.md"


def test_ci_workflow_has_backend_frontend_and_compose_gates() -> None:
    text = CI.read_text(encoding="utf-8")

    for marker in (
        "backend-and-quality:",
        "python -m pytest",
        "frontend:",
        "npm ci",
        "npm run build",
        "compose-config:",
        "docker compose --env-file infra/dev/.env.example",
        "docker compose --env-file infra/test/.env.example",
        "docker compose --env-file infra/stage/.env.example",
    ):
        assert marker in text


def test_release_notes_template_requires_traceability_and_rollback() -> None:
    text = RELEASE_TEMPLATE.read_text(encoding="utf-8")

    for marker in (
        "Commit SHA",
        "Gates",
        "Migration dry-run",
        "Risk And Rollback",
        "Rollback trigger",
        "Approval",
    ):
        assert marker in text


def test_release_strategy_mentions_security_and_network_quality_gates() -> None:
    text = (ROOT / "RELEASE_GATE_STRATEGY.md").read_text(encoding="utf-8")

    assert "tests/quality/test_no_committed_secrets.py" in text
    assert "tests/quality/test_no_hardcoded_network_config.py" in text
    assert "tests/quality/test_text_encoding.py" in text
