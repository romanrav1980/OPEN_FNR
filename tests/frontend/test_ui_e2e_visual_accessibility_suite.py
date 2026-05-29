from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MAIN = ROOT / "apps" / "frontend" / "src" / "main.tsx"
REPORTS = ROOT / "docs" / "test-reports"


def _main_text() -> str:
    return MAIN.read_text(encoding="utf-8")


def test_pilot_critical_routes_and_sections_have_static_e2e_coverage() -> None:
    text = _main_text()

    for marker in (
        "#/control-tower",
        "#/data",
        "#/forecast",
        "#/replenishment",
        "#/operations",
        "#/admin",
        "#/process-navigator",
        "Forecast Workbench",
        "Integration Operations Console",
        "Replenishment Workbench",
        "Admin Console V1",
        "Process Navigator",
    ):
        assert marker in text


def test_accessibility_foundation_markers_are_present() -> None:
    text = _main_text()
    supplement = (ROOT / "PROCESS_NAVIGATOR_MAP_SPEC_SUPPLEMENT_1.md").read_text(encoding="utf-8")

    assert "function HelpFootnote" in text
    assert "aria-label=" in text
    assert 'type="button"' in text
    assert 'event.key === "Escape"' in text
    assert "Keyboard navigation" in supplement
    assert "WCAG 2.1 Level AA" in supplement
    assert "prefers-reduced-motion" in (ROOT / "apps" / "frontend" / "src" / "styles.css").read_text(encoding="utf-8")


def test_ui_actions_expose_loading_fallback_error_or_blocked_context() -> None:
    text = _main_text()

    for marker in (
        "fallback",
        "blocked",
        "Error State",
        "Denied State",
        "Blocking DQ incidents stop publication",
        "Manual review because the projection has stock-out risk",
    ):
        assert marker in text


def test_ui_evidence_reports_exist_for_productization_sprints() -> None:
    expected_reports = (
        "sprint-ui-1-routed-foundation/index.html",
        "sprint-ui-2-forecast-replenishment-workbenches/index.html",
        "sprint-ui-3-integration-data-quality/index.html",
        "sprint-ui-4-security-admin-process/index.html",
        "sprint-ui-5-e2e-visual-accessibility/index.html",
    )

    for report in expected_reports:
        path = REPORTS / report
        assert path.exists(), f"missing UI evidence report: {report}"
        assert "<html" in path.read_text(encoding="utf-8").lower()


def test_ui_suite_avoids_hardcoded_network_strings() -> None:
    text = _main_text()

    for forbidden in ("http://localhost", "127.0.0.1"):
        assert forbidden not in text
