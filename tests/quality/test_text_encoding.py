from pathlib import Path


TEXT_EXTENSIONS = {
    ".css",
    ".html",
    ".json",
    ".md",
    ".py",
    ".toml",
    ".ts",
    ".tsx",
    ".xml",
    ".yaml",
    ".yml",
}

EXCLUDED_DIRS = {
    ".git",
    ".pytest_cache",
    ".venv",
    "dist",
    "node_modules",
}

# Written as Unicode escapes so this quality gate cannot become mojibake itself.
MOJIBAKE_MARKERS = (
    "\u0420\u045f",
    "\u0420\u045e",
    "\u0420\u0459",
    "\u0420\u203a",
    "\u0420\u045c",
    "\u0420\u0491",
    "\u0420\u00bb",
    "\u0420\u00b5",
    "\u0420\u0455",
    "\u0420\u00b0",
    "\u0421\u0453",
    "\u0421\u201a",
    "\u0421\u0152",
    "\u00d0",
    "\u00d1",
)


def iter_text_files() -> list[Path]:
    files: list[Path] = []
    for path in Path(".").rglob("*"):
        if not path.is_file():
            continue
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in TEXT_EXTENSIONS:
            files.append(path)
    return files


def test_text_files_are_utf8_decodable() -> None:
    broken: list[str] = []
    for path in iter_text_files():
        try:
            path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            broken.append(f"{path}: {exc}")

    assert broken == []


def test_text_files_do_not_contain_common_mojibake_markers() -> None:
    broken: list[str] = []
    for path in iter_text_files():
        text = path.read_text(encoding="utf-8")
        for marker in MOJIBAKE_MARKERS:
            if marker in text:
                broken.append(f"{path}: marker {marker!r}")
                break

    assert broken == []
