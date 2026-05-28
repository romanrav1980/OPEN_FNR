from datetime import date

from open_fnr_api.feature_mart import ACTIVE_MATRIX, FEATURES, feature_build_plan_for_date


def test_active_matrix_excludes_inactive_entities() -> None:
    assert all(item.excluded_closed_stores >= 0 for item in ACTIVE_MATRIX)
    assert all(item.excluded_inactive_skus >= 0 for item in ACTIVE_MATRIX)
    assert all(item.active_pairs <= item.stores * item.skus for item in ACTIVE_MATRIX)


def test_no_feature_leakage_in_registered_features() -> None:
    assert all(feature.point_in_time_safe for feature in FEATURES)


def test_feature_build_plan_requires_published_clean_inputs() -> None:
    plan = feature_build_plan_for_date(date(2026, 5, 28))
    assert plan.dependency_count == len(plan.dependencies)
    assert all(dependency.status == "published" for dependency in plan.dependencies)
    assert all(dependency.freshness_status == "fresh" for dependency in plan.dependencies)
    assert "no_future_fact_leakage" in plan.validation_rules
