from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MAIN = ROOT / "apps" / "frontend" / "src" / "main.tsx"


def _main_text() -> str:
    return MAIN.read_text(encoding="utf-8")


def test_forecast_and_promo_workbench_sections_are_present() -> None:
    text = _main_text()

    for marker in (
        "Forecast Workbench",
        "Promo Workbench Draft",
        "Promo Forecast V1",
        "Required Promo Fields",
        "Regular baseline + promo uplift = total forecast",
        "Reference promo",
    ):
        assert marker in text


def test_replenishment_projection_and_order_workbench_sections_are_present() -> None:
    text = _main_text()

    for marker in (
        "Inventory Projection",
        "Projected stock, demand projection, open orders, in-transit and safety threshold",
        "Order Proposal V1",
        "Replenishment Workbench",
        "Planner workspace for final order review, adjustment, approval and audit",
        "Manual Adjustments",
    ):
        assert marker in text


def test_workbench_ui_uses_shared_api_configuration() -> None:
    text = _main_text()

    assert "apiUrl(" in text
    assert "from \"./app_config\"" in text
    assert "http://localhost" not in text
    assert "127.0.0.1" not in text


def test_planner_actions_expose_process_audit_and_validation_context() -> None:
    text = _main_text()

    for marker in (
        "audit trail",
        "writes old/new quantities to audit",
        "requires a reason and comment",
        "Original ML forecast remains unchanged",
        "Manual review because the projection has stock-out risk",
        "Promo cannot move to forecast until required commercial and display attributes are complete",
    ):
        assert marker in text


def test_workbench_sections_are_accessibly_labeled() -> None:
    text = _main_text()

    for aria_label in (
        'aria-label="Promo workbench"',
        'aria-label="Promo forecast"',
        'aria-label="Inventory projection"',
        'aria-label="Manual adjustments"',
    ):
        assert aria_label in text
