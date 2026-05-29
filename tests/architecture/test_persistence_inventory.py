from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INVENTORY = ROOT / "docs" / "persistence" / "PERSISTENCE_INVENTORY.md"

REQUIRED_PRODUCTION_MODULES = {
    "adjustments.py": "AdjustmentRepository",
    "exceptions.py": "ExceptionRepository",
    "process_engine.py": "ProcessTaskRepository",
    "publication.py": "PublicationPackageRepository",
    "replenishment.py": "OrderProposalRepository",
    "security.py": "UserRepository",
    "store_management.py": "StoreTaskRepository",
}

REQUIRED_SECTIONS = (
    "## 2. Classification",
    "## 4. P0/P1 Production Persistence Targets",
    "## 7. IH-2 Migration Order",
    "## 8. Repository Interface Standard",
)


def test_persistence_inventory_exists_and_has_required_sections() -> None:
    text = INVENTORY.read_text(encoding="utf-8")

    for section in REQUIRED_SECTIONS:
        assert section in text


def test_persistence_inventory_tracks_core_production_state() -> None:
    text = INVENTORY.read_text(encoding="utf-8")

    for module_name, repository_name in REQUIRED_PRODUCTION_MODULES.items():
        assert module_name in text
        assert repository_name in text


def test_persistence_inventory_defines_mock_mode_boundary() -> None:
    text = INVENTORY.read_text(encoding="utf-8")

    assert "OPEN_FNR_MOCK_MODE=true" in text
    assert "process business audit remains enabled by default" in text
