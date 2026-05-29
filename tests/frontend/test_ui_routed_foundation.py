from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MAIN = ROOT / "apps" / "frontend" / "src" / "main.tsx"
CONFIG = ROOT / "apps" / "frontend" / "src" / "app_config.ts"


def test_frontend_declares_required_workspace_routes() -> None:
    text = MAIN.read_text(encoding="utf-8")

    for route in (
        "#/control-tower",
        "#/data",
        "#/forecast",
        "#/replenishment",
        "#/operations",
        "#/admin",
        "#/process-navigator",
    ):
        assert route in text


def test_frontend_route_state_uses_hash_change_listener() -> None:
    text = MAIN.read_text(encoding="utf-8")

    assert "routeFromHash(window.location.hash)" in text
    assert 'window.addEventListener("hashchange", handleHashChange)' in text
    assert 'window.removeEventListener("hashchange", handleHashChange)' in text


def test_frontend_uses_central_api_configuration_and_help_footnotes() -> None:
    main_text = MAIN.read_text(encoding="utf-8")
    config_text = CONFIG.read_text(encoding="utf-8")

    assert 'from "./app_config"' in main_text
    assert "apiUrl(" in main_text
    assert "localServiceUrl(" in main_text
    assert "function HelpFootnote" in main_text
    assert "links:" in main_text
    assert "VITE_OPEN_FNR_SERVICE_HOST" in config_text
    assert "VITE_OPEN_FNR_API_PORT" in config_text
