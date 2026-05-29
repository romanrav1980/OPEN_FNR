from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
ALLOWED_SECRET_REFERENCE_FILES = {
    ".env.example",
    "CONFIGURATION_MANIFEST.md",
    "SECRET_MANAGEMENT_SPEC.md",
    "SECURITY_STRATEGY.md",
    "apps/backend/open_fnr_api/config.py",
    "apps/backend/open_fnr_api/security.py",
    "apps/frontend/.env.example",
    "infra/dev/.env.example",
    "infra/test/.env.example",
    "infra/stage/.env.example",
    "tests/quality/test_no_committed_secrets.py",
}
SECRET_NAME_PATTERN = re.compile(r"(?i)(password|secret|private[_-]?key|api[_-]?key)\s*=\s*[\"'][^\"']+[\"']")
PRIVATE_KEY_PATTERN = re.compile(r"-----BEGIN (RSA |EC |OPENSSH |)PRIVATE KEY-----")


def _tracked_text_files() -> list[Path]:
    candidates: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT).as_posix()
        if any(part in {".git", "__pycache__", "node_modules", "dist", ".pytest_cache", "tmp"} for part in path.parts):
            continue
        if path.suffix.lower() in {".py", ".md", ".txt", ".yaml", ".yml", ".json", ".toml", ".env", ".example", ".ps1"} or path.name.endswith(".example"):
            candidates.append(path)
    return candidates


def test_no_local_env_or_key_files_are_committed() -> None:
    forbidden_names = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT).as_posix()
        if relative.endswith(".env.example") or relative.endswith(".example"):
            continue
        if path.name in {".env", ".env.local"} or path.suffix.lower() in {".pem", ".key"}:
            forbidden_names.append(relative)

    assert forbidden_names == []


def test_no_private_key_material_is_present() -> None:
    offenders = []
    for path in _tracked_text_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        if PRIVATE_KEY_PATTERN.search(text):
            offenders.append(path.relative_to(ROOT).as_posix())

    assert offenders == []


def test_secret_assignments_are_limited_to_configuration_manifests_and_examples() -> None:
    offenders = []
    for path in _tracked_text_files():
        relative = path.relative_to(ROOT).as_posix()
        if relative.startswith("tests/"):
            continue
        if relative in ALLOWED_SECRET_REFERENCE_FILES:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if SECRET_NAME_PATTERN.search(text):
            offenders.append(relative)

    assert offenders == []


def test_gitignore_blocks_common_secret_artifacts() -> None:
    text = (ROOT / ".gitignore").read_text(encoding="utf-8")

    for pattern in (".env", ".env.local", "*.pem", "*.key", "secrets/"):
        assert pattern in text
