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
