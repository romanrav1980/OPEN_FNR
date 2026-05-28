from datetime import date
from pathlib import Path

from open_fnr_api.pilot_fixtures import generate_pilot_landing_pack
from open_fnr_api.shadow_load import run_shadow_load_discovery


def test_pilot_landing_pack_generates_all_source_contract_files(tmp_path) -> None:
    result = generate_pilot_landing_pack(tmp_path, date(2026, 5, 28))

    assert len(result.files) == 9
    assert all(Path(item.file_path).exists() for item in result.files)
    assert all(Path(item.manifest_path).exists() for item in result.files)
    report = run_shadow_load_discovery(date(2026, 5, 28), tmp_path)
    assert report.status == "ready_for_validation"
    assert report.discovered_contracts == 9
