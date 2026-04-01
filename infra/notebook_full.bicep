targetScope = 'resourceGroup'

// Tier 3 resources: Days 8-10
// ACR · Key Vault · Log Analytics · Application Insights · ACA environment
// Managed identities · Azure Machine Learning

param location string
param acrName string
param keyVaultName string
param logAnalyticsName string
param appInsightsName string
param containerAppsEnvName string
param mlWorkspaceName string

@description('Storage account name created in Tier 1 (core) — passed to Azure ML as an associated resource')
param storageAccountName string

param workloadIdentityName string
param jobsIdentityName string
param searchAdminIdentityName string

// ── Log Analytics Workspace ───────────────────────────────────────────────────

resource law 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: logAnalyticsName
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

// ── Application Insights ──────────────────────────────────────────────────────

resource appi 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: law.id
  }
}

// ── Container Registry ────────────────────────────────────────────────────────

resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: acrName
  location: location
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: false
  }
}

// ── Key Vault ─────────────────────────────────────────────────────────────────

resource kv 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  properties: {
    enableRbacAuthorization: true
    publicNetworkAccess: 'Enabled'
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
  }
}

// ── Container Apps Environment ────────────────────────────────────────────────

resource cae 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: containerAppsEnvName
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: law.properties.customerId
        sharedKey: law.listKeys().primarySharedKey
      }
    }
  }
}

// ── Workload managed identities ───────────────────────────────────────────────

resource workloadIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: workloadIdentityName
  location: location
}

resource jobsIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: jobsIdentityName
  location: location
}

resource searchAdminIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: searchAdminIdentityName
  location: location
}

// ── Azure Machine Learning Workspace (Days 8-10 — stub) ──────────────────────
// Requires storage, key vault, and app insights as associated resources.
// The storage account was created by the core tier; reference it here.

resource storageExisting 'Microsoft.Storage/storageAccounts@2025-06-01' existing = {
  name: storageAccountName
}

module mlWorkspace './modules/azure_ml.bicep' = {
  name: '${deployment().name}-ml'
  params: {
    mlWorkspaceName: mlWorkspaceName
    location: location
    storageAccountId: storageExisting.id
    keyVaultId: kv.id
    appInsightsId: appi.id
  }
}

// ── Outputs ───────────────────────────────────────────────────────────────────

output AZURE_KEY_VAULT_URI string = kv.properties.vaultUri
output AZURE_ACR_LOGIN_SERVER string = acr.properties.loginServer
output AZURE_CONTAINER_APPS_ENVIRONMENT_ID string = cae.id
output APPLICATIONINSIGHTS_CONNECTION_STRING string = appi.properties.ConnectionString
output AZURE_ML_WORKSPACE_ID string = mlWorkspace.outputs.mlWorkspaceId
output AZURE_LOG_ANALYTICS_WORKSPACE_ID string = law.id
output WORKLOAD_IDENTITY_CLIENT_ID string = workloadIdentity.properties.clientId
output WORKLOAD_IDENTITY_PRINCIPAL_ID string = workloadIdentity.properties.principalId
output JOBS_IDENTITY_CLIENT_ID string = jobsIdentity.properties.clientId
output SEARCH_ADMIN_IDENTITY_CLIENT_ID string = searchAdminIdentity.properties.clientId
