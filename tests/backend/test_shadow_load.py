from datetime import date

from open_fnr_api.shadow_load import SOURCE_MANIFESTS, run_shadow_load_discovery


def test_shadow_load_discovery_reports_missing_contracts(tmp_path) -> None:
    source_dir = tmp_path / "pos" / "pos_sales_line" / "business_date=2026-05-28"
    source_dir.mkdir(parents=True)
    (source_dir / "sales.csv").write_text("receipt_id,line_id\nr1,1\n", encoding="utf-8")

    report = run_shadow_load_discovery(date(2026, 5, 28), tmp_path)

    assert report.status == "incomplete"
    assert report.total_contracts == len(SOURCE_MANIFESTS)
    assert report.discovered_contracts == 1
    assert report.missing_contracts == len(SOURCE_MANIFESTS) - 1
    pos_result = next(result for result in report.results if result.contract_name == "pos_sales_line")
    assert pos_result.status == "discovered"
    assert pos_result.discovered_file_count == 1


def test_shadow_load_discovery_is_ready_when_all_contracts_have_files(tmp_path) -> None:
    business_date = date(2026, 5, 28)
    for manifest in SOURCE_MANIFESTS:
        source_dir = (
            tmp_path
            / manifest.source_system.lower()
            / manifest.contract_name
            / f"business_date={business_date.isoformat()}"
        )
        source_dir.mkdir(parents=True)
        (source_dir / f"{manifest.contract_name}.json").write_text("{}", encoding="utf-8")

    report = run_shadow_load_discovery(business_date, tmp_path)

    assert report.status == "ready_for_validation"
    assert report.discovered_contracts == report.total_contracts
    assert report.missing_contracts == 0
    assert all(result.idempotency_key.endswith(":2026-05-28") for result in report.results)
