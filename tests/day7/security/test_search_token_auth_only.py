from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def test_container_app_contract_does_not_inject_search_keys() -> None:
    template = (ROOT / "infra" / "modules" / "container_app.bicep").read_text(encoding="utf-8")

    assert "SystemAssigned,UserAssigned" in template
    assert "AEGISAP_RESUME_TOKEN_SECRET_NAME" in template
    assert "name: 'AEGISAP_RESUME_TOKEN_SECRET'" not in template
    assert "secretRef: 'resume-token-secret'" not in template
    assert "SEARCH_ADMIN_KEY" not in template
    assert "SEARCH_QUERY_KEY" not in template


def test_full_bicep_keeps_search_local_auth_disabled() -> None:
    full_template = (ROOT / "infra" / "full.bicep").read_text(encoding="utf-8")
    core_template = (ROOT / "infra" / "core.bicep").read_text(encoding="utf-8")
    search_template = (ROOT / "infra" / "foundations" / "search_service.bicep").read_text(encoding="utf-8")

    assert "module core './core.bicep'" in full_template
    assert "module search './foundations/search_service.bicep'" in core_template
    assert "disableLocalAuth: true" in search_template


def test_role_assignments_keep_runtime_search_access_reader_only() -> None:
    template = (ROOT / "infra" / "modules" / "role_assignments.bicep").read_text(encoding="utf-8")

    assert "searchIndexDataReaderRoleDefinitionId" in template
    assert "name: guid(searchService.id, runtimeApiPrincipalId, searchIndexDataReaderRoleDefinitionId)" in template
    assert "name: guid(searchService.id, runtimeApiPrincipalId, searchIndexDataContributorRoleDefinitionId)" not in template
    assert "name: guid(searchService.id, searchAdminIdentityPrincipalId, searchIndexDataContributorRoleDefinitionId)" in template


def test_key_vault_diagnostics_module_is_wired() -> None:
    module_template = (ROOT / "infra" / "foundations" / "diagnostic_settings.bicep").read_text(encoding="utf-8")
    full_template = (ROOT / "infra" / "full.bicep").read_text(encoding="utf-8")

    assert "AuditEvent" in module_template
    assert "module keyVaultDiagnostics './foundations/diagnostic_settings.bicep'" in full_template
