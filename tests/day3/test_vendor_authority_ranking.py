from pathlib import Path

from aegisap.day3.retrieval.authority_policy import load_authority_policy
from aegisap.day3.retrieval.azure_ai_search_adapter import AzureAISearchFixtureAdapter
from aegisap.day3.retrieval.ranker import apply_authority_ranking
from aegisap.day3.retrieval.structured_vendor_lookup import StructuredVendorLookup


def test_structured_vendor_master_outranks_old_email_for_bank_details():
    policy = load_authority_policy(
        Path("src/aegisap/day3/policies/source_authority_rules.yaml")
    )
    structured = StructuredVendorLookup().search(vendor_id="VEND-001", vendor_name=None)
    unstructured = AzureAISearchFixtureAdapter().search(
        query="Acme Office Supplies bank change 4421"
    )

    ranked = apply_authority_ranking(
        structured + unstructured,
        policy=policy,
        query_terms={"bank_account_last4": "4421"},
    )

    assert ranked[0].source_type == "erp_vendor_master"
    assert ranked[0].metadata["bank_account_last4"] == "4421"
    assert any(item.metadata.get("bank_account_last4") == "1138" for item in ranked)


def test_policy_file_loads_from_day3_package_location():
    policy = load_authority_policy(Path("src/aegisap/day3/policies/source_authority_rules.yaml"))

    assert policy["authority_weights"][1] == 1.6
    assert "bank_account_last4" in policy["authority_rules"]
