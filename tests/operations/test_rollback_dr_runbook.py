from pathlib import Path


RUNBOOK = Path("docs/runbooks/ROLLBACK_DR_DRILL_RUNBOOK.md")


def test_rollback_dr_runbook_covers_recovery_and_degraded_mode() -> None:
    text = RUNBOOK.read_text(encoding="utf-8")

    assert "Freeze controlled exports" in text
    assert "Restore the previous approved application version" in text
    assert "migration rollback or forward-fix" in text
    assert "Validate backup/restore smoke evidence" in text
    assert "shadow_review_only" in text
    assert "ERP export" in text
    assert "RPO/RTO" in text
