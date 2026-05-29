from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BACKUP_SCRIPT = ROOT / "scripts" / "dev" / "backup-smoke.ps1"
RESTORE_SCRIPT = ROOT / "scripts" / "dev" / "restore-smoke.ps1"
RUNBOOK = ROOT / "docs" / "runbooks" / "BACKUP_RESTORE_RUNBOOK.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_backup_and_restore_smoke_scripts_exist() -> None:
    assert BACKUP_SCRIPT.exists()
    assert RESTORE_SCRIPT.exists()
    assert RUNBOOK.exists()


def test_backup_script_uses_central_configuration_and_checksum() -> None:
    text = _read(BACKUP_SCRIPT)

    for name in (
        "OPEN_FNR_BACKUP_ROOT_PATH",
        "OPEN_FNR_POSTGRES_HOST",
        "OPEN_FNR_POSTGRES_PORT",
        "OPEN_FNR_POSTGRES_DATABASE",
        "OPEN_FNR_CLICKHOUSE_HOST",
        "OPEN_FNR_CLICKHOUSE_HTTP_PORT",
        "OPEN_FNR_CLICKHOUSE_DATABASE",
    ):
        assert name in text

    assert "Get-FileHash -Algorithm SHA256" in text
    assert '[string]$Mode = "plan"' in text


def test_restore_script_is_guarded_and_verifies_manifest_checksum() -> None:
    text = _read(RESTORE_SCRIPT)

    assert '[string]$Mode = "plan"' in text
    assert "ManifestPath is required in execute mode" in text
    assert "OPEN_FNR_RESTORE_POSTGRES_DATABASE" in text
    assert "OPEN_FNR_RESTORE_CLICKHOUSE_DATABASE" in text
    assert "PostgreSQL dump checksum does not match manifest" in text


def test_backup_restore_scripts_do_not_embed_network_defaults() -> None:
    combined = "\n".join((_read(BACKUP_SCRIPT), _read(RESTORE_SCRIPT), _read(RUNBOOK)))

    forbidden_fragments = (
        "127.0.0.1",
        "localhost",
        ":5432",
        ":8123",
        ":15432",
        ":18123",
        "http://",
        "https://",
    )

    for fragment in forbidden_fragments:
        assert fragment not in combined
