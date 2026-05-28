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

MOJIBAKE_MARKERS = (
    "Рџ",
    "РЎ",
    "Рќ",
    "Рґ",
    "Р»",
    "Рµ",
    "Рѕ",
    "Р°",
    "СЃ",
    "С‚",
    "СЊ",
    "Р ",
    "Р",
    "Ð",
    "Ñ",
)


def iter_text_files() -> list[Path]:
    files: list[Path] = []
    for path in Path(".").rglob("*"):
        if not path.is_file():
            continue
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        if path == Path("tests/quality/test_text_encoding.py"):
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
