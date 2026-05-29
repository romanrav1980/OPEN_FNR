from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INFRA = ROOT / "infra"


def _env_lines(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key] = value
    return values


def test_all_environment_templates_exist() -> None:
    for environment in ("dev", "test", "stage", "prod"):
        assert (INFRA / environment / ".env.example").exists()
        assert (INFRA / environment / "README.md").exists()


def test_prod_template_disables_mock_and_dev_auth_bypass() -> None:
    prod = _env_lines(INFRA / "prod" / ".env.example")

    assert prod["OPEN_FNR_RUNTIME_MODE"] == "prod"
    assert prod["OPEN_FNR_MOCK_MODE"] == "false"
    assert prod["OPEN_FNR_AUTH_ENABLED"] == "true"
    assert prod["OPEN_FNR_AUTH_DEV_BYPASS_ENABLED"] == "false"
    assert prod["OPEN_FNR_AUDIT_ENABLED"] == "true"


def test_prod_template_does_not_commit_secret_values() -> None:
    prod = _env_lines(INFRA / "prod" / ".env.example")
    secret_keys = [key for key in prod if "PASSWORD" in key or "SECRET" in key or "PRIVATE_KEY" in key or key.endswith("_KEY")]

    assert secret_keys
    assert all(prod[key] == "" for key in secret_keys)


def test_stage_and_prod_do_not_enable_dev_bypass() -> None:
    stage = _env_lines(INFRA / "stage" / ".env.example")
    prod = _env_lines(INFRA / "prod" / ".env.example")

    assert stage["OPEN_FNR_AUTH_DEV_BYPASS_ENABLED"] == "false"
    assert prod["OPEN_FNR_AUTH_DEV_BYPASS_ENABLED"] == "false"
