from open_fnr_api.feature_mart import ACTIVE_MATRIX, FEATURES


def test_active_matrix_excludes_inactive_entities() -> None:
    assert all(item.excluded_closed_stores >= 0 for item in ACTIVE_MATRIX)
    assert all(item.excluded_inactive_skus >= 0 for item in ACTIVE_MATRIX)
    assert all(item.active_pairs <= item.stores * item.skus for item in ACTIVE_MATRIX)


def test_no_feature_leakage_in_registered_features() -> None:
    assert all(feature.point_in_time_safe for feature in FEATURES)
