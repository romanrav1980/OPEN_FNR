from open_fnr_api.data_contracts import SOURCE_CONTRACT_MODELS, SOURCE_CONTRACT_REGISTRY
from open_fnr_api.ingestion import PILOT_REQUIRED_SOURCE_CONTRACTS


def test_ri1_source_contract_registry_covers_every_pilot_required_contract() -> None:
    frozen_names = {contract.contract_name for contract in SOURCE_CONTRACT_REGISTRY}
    required_names = {contract.contract_name for contract in PILOT_REQUIRED_SOURCE_CONTRACTS}

    assert required_names == frozen_names


def test_ri1_every_frozen_contract_has_model_owner_sla_and_reconciliation_keys() -> None:
    for contract in SOURCE_CONTRACT_REGISTRY:
        assert contract.contract_name in SOURCE_CONTRACT_MODELS
        assert contract.model_name == SOURCE_CONTRACT_MODELS[contract.contract_name].__name__
        assert contract.contract_version == "v1"
        assert contract.business_owner_role
        assert contract.technical_owner_role
        assert contract.source_sla
        assert contract.freshness_field
        assert contract.primary_key
        assert contract.required_fields
        assert contract.idempotency_fields
        assert contract.reconciliation_keys
        assert contract.required_for
        assert contract.blocking_dq_checks


def test_ri1_contracts_define_expected_business_coverage() -> None:
    coverage = {item for contract in SOURCE_CONTRACT_REGISTRY for item in contract.required_for}

    assert "regular_forecast" in coverage
    assert "promo_forecast" in coverage
    assert "projected_stock" in coverage
    assert "replenishment" in coverage
    assert "publication_reconciliation" in coverage
    assert "display_capacity" in coverage
