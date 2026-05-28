from datetime import date

from open_fnr_api.source_adapters import LocalFileDropAdapter


def test_local_file_drop_adapter_discovers_supported_files(tmp_path) -> None:
    source_dir = tmp_path / "pos" / "pos_sales_line" / "business_date=2026-05-28"
    source_dir.mkdir(parents=True)
    supported = source_dir / "sales.parquet"
    ignored = source_dir / "readme.txt"
    supported.write_bytes(b"sample")
    ignored.write_text("ignore", encoding="utf-8")

    adapter = LocalFileDropAdapter(tmp_path)
    files = adapter.discover("POS", "pos_sales_line", date(2026, 5, 28))

    assert len(files) == 1
    assert files[0].source_system == "POS"
    assert files[0].contract_name == "pos_sales_line"
    assert files[0].file_name == "sales.parquet"
    assert files[0].size_bytes == 6


def test_local_file_drop_adapter_loads_manifest_sidecar(tmp_path) -> None:
    source_dir = tmp_path / "pos" / "pos_sales_line" / "business_date=2026-05-28"
    source_dir.mkdir(parents=True)
    (source_dir / "manifest.json").write_text(
        """
        {
          "source_system": "POS",
          "contract_name": "pos_sales_line",
          "business_date": "2026-05-28",
          "row_count": 2,
          "checksum": "sha256:test",
          "idempotency_key": "POS:pos_sales_line:v1:2026-05-28",
          "files": ["sales.csv"]
        }
        """,
        encoding="utf-8",
    )

    adapter = LocalFileDropAdapter(tmp_path)
    manifest = adapter.load_manifest_sidecar("POS", "pos_sales_line", date(2026, 5, 28))

    assert manifest is not None
    assert manifest.row_count == 2
    assert manifest.checksum == "sha256:test"


def test_local_file_drop_adapter_does_not_treat_manifest_as_source_file(tmp_path) -> None:
    source_dir = tmp_path / "pos" / "pos_sales_line" / "business_date=2026-05-28"
    source_dir.mkdir(parents=True)
    (source_dir / "manifest.json").write_text(
        """
        {
          "source_system": "POS",
          "contract_name": "pos_sales_line",
          "business_date": "2026-05-28",
          "row_count": 1,
          "checksum": "sha256:test",
          "idempotency_key": "POS:pos_sales_line:v1:2026-05-28",
          "files": ["sales.json"]
        }
        """,
        encoding="utf-8",
    )
    (source_dir / "sales.json").write_text('{"ok": true}', encoding="utf-8")

    adapter = LocalFileDropAdapter(tmp_path)
    files = adapter.discover("POS", "pos_sales_line", date(2026, 5, 28))

    assert len(files) == 1
    assert files[0].file_name == "sales.json"
