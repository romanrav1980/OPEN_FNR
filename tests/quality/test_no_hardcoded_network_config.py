from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
SCANNED_ROOTS = (
    ROOT / "apps" / "backend" / "open_fnr_api",
    ROOT / "apps" / "frontend" / "src",
)
ALLOWED_FILES = {
    ROOT / "apps" / "backend" / "open_fnr_api" / "config.py",
    ROOT / "apps" / "frontend" / "src" / "app_config.ts",
}
NETWORK_PATTERN = re.compile(
    r"(127\.0\.0\.1|localhost|:(8000|13000|15432|18123|18080|18088|19200|15601|18089)\b)"
)


def test_application_code_does_not_hardcode_network_addresses() -> None:
    offenders: list[str] = []
    for scanned_root in SCANNED_ROOTS:
        for path in scanned_root.rglob("*"):
            if path in ALLOWED_FILES or path.suffix not in {".py", ".ts", ".tsx"}:
                continue
            text = path.read_text(encoding="utf-8")
            if NETWORK_PATTERN.search(text):
                offenders.append(str(path.relative_to(ROOT)))

    assert offenders == []
