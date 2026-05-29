from datetime import date

from fastapi.testclient import TestClient

from open_fnr_api.data_quality import run_source_contract_dq
from open_fnr_api.main import app
from open_fnr_api.shadow_load import SOURCE_MANIFESTS, run_shadow_load_discovery


client = TestClient(app)


def test_source_contract_dq_blocks_missing_files(tmp_path) -> None:
    report = run_shadow_load_discovery(date(2026, 5, 28), tmp_path)
    result = run_source_contract_dq(report)

    assert result.status == "blocked"
    assert result.total_contracts == len(SOURCE_MANIFESTS)
    assert result.blocker_count == len(SOURCE_MANIFESTS)
    assert all(item.status == "blocked" for item in result.results)


def test_source_contract_dq_passes_when_all_files_are_present(tmp_path) -> None:
    business_date = date(2026, 5, 28)
    for manifest in SOURCE_MANIFESTS:
        source_dir = (
            tmp_path
            / manifest.source_system.lower()
            / manifest.contract_name
            / f"business_date={business_date.isoformat()}"
        )
        source_dir.mkdir(parents=True)
        (source_dir / f"{manifest.contract_name}.json").write_text('{"ok": true}', encoding="utf-8")

    report = run_shadow_load_discovery(business_date, tmp_path)
    result = run_source_contract_dq(report)

    assert result.status == "passed"
    assert result.blocker_count == 0
    assert result.warning_count == 0
    assert all(item.blocking_rules_checked for item in result.results)


def test_source_contract_dq_api_runs_against_landing_path(tmp_path) -> None:
    response = client.post(
        "/data-quality/source-contract-runs",
        json={"business_date": "2026-05-28", "landing_root_path": str(tmp_path)},
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] == "blocked"
    assert payload["blocker_count"] == len(SOURCE_MANIFESTS)
    assert payload["results"][0]["severity"] == "blocker"
