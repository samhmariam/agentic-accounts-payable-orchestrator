targetScope = 'resourceGroup'

@description('Primary region')
param location string = resourceGroup().location

@description('Storage account name')
param storageAccountName string

@description('Blob container name for source documents')
param storageContainerName string = 'documents'

@description('Container registry name')
param acrName string

@description('Search service name')
param searchName string

@description('Starter search index name for Day 0')
param searchIndexName string = 'documents'

@description('PostgreSQL server name')
param postgresServerName string

@description('PostgreSQL application database name')
param postgresDatabaseName string = 'aegisap'

@description('Key Vault name')
param keyVaultName string

@description('Microsoft Foundry resource name')
param openAiName string

@description('OpenAI-compatible API version exported into the local environment')
param openAiApiVersion string = '2024-08-01-preview'

@description('OpenAI-compatible chat deployment name exported into the local environment')
param openAiChatDeploymentName string

@description('Optional OpenAI-compatible chat model name for automatic deployment creation')
param openAiChatModelName string = ''

@description('Optional OpenAI-compatible chat model version for automatic deployment creation')
param openAiChatModelVersion string = ''

@description('Optional chat deployment SKU name')
param openAiChatSkuName string = 'Standard'

@description('Optional chat deployment capacity')
param openAiChatCapacity int = 0

@description('Log Analytics workspace name')
param logAnalyticsName string

@description('Application Insights name')
param appInsightsName string

@description('Container Apps environment name')
param containerAppsEnvName string

@description('Object ID of the PostgreSQL Microsoft Entra admin principal')
param postgresEntraAdminObjectId string

@description('Name of the PostgreSQL Microsoft Entra admin principal')
param postgresEntraAdminName string

@allowed([
  'User'
  'ServicePrincipal'
  'Group'
  'Unknown'
])
@description('Principal type for the PostgreSQL Microsoft Entra admin')
param postgresEntraAdminType string = 'User'

@description('User-assigned managed identity name used for registry pull and Key Vault secret references')
param workloadIdentityName string = 'id-aegisap-workload'

@description('User-assigned managed identity name scaffolded for background jobs and replay workers')
param jobsIdentityName string = 'id-aegisap-jobs'

@description('User-assigned managed identity name scaffolded for Search indexing and schema administration')
param searchAdminIdentityName string = 'id-aegisap-search-admin'

module core './core.bicep' = {
  name: '${deployment().name}-core'
  params: {
    location: location
    storageAccountName: storageAccountName
    storageContainerName: storageContainerName
    searchName: searchName
    searchIndexName: searchIndexName
    openAiName: openAiName
    openAiApiVersion: openAiApiVersion
    openAiChatDeploymentName: openAiChatDeploymentName
    openAiChatModelName: openAiChatModelName
    openAiChatModelVersion: openAiChatModelVersion
    openAiChatSkuName: openAiChatSkuName
    openAiChatCapacity: openAiChatCapacity
  }
}

module acr './foundations/container_registry.bicep' = {
  name: '${deployment().name}-acr'
  params: {
    location: location
    acrName: acrName
  }
}

module observability './foundations/observability.bicep' = {
  name: '${deployment().name}-observability'
  params: {
    location: location
    logAnalyticsName: logAnalyticsName
    appInsightsName: appInsightsName
  }
}

module identities './foundations/managed_identities.bicep' = {
  name: '${deployment().name}-identities'
  params: {
    location: location
    workloadIdentityName: workloadIdentityName
    jobsIdentityName: jobsIdentityName
    searchAdminIdentityName: searchAdminIdentityName
  }
}

module containerAppsEnv './foundations/aca_environment.bicep' = {
  name: '${deployment().name}-cae'
  dependsOn: [observability]
  params: {
    location: location
    containerAppsEnvName: containerAppsEnvName
    logAnalyticsWorkspaceName: logAnalyticsName
  }
}

module postgres './foundations/postgres_server.bicep' = {
  name: '${deployment().name}-postgres'
  params: {
    location: location
    postgresServerName: postgresServerName
    postgresDatabaseName: postgresDatabaseName
    postgresEntraAdminObjectId: postgresEntraAdminObjectId
    postgresEntraAdminName: postgresEntraAdminName
    postgresEntraAdminType: postgresEntraAdminType
  }
}

module keyVault './foundations/key_vault.bicep' = {
  name: '${deployment().name}-keyvault'
  params: {
    location: location
    keyVaultName: keyVaultName
  }
}

module keyVaultDiagnostics './foundations/diagnostic_settings.bicep' = {
  name: 'keyVaultDiagnostics'
  dependsOn: [
    keyVault
    observability
  ]
  params: {
    keyVaultName: keyVaultName
    logAnalyticsWorkspaceName: logAnalyticsName
  }
}

module day8Alerts './monitoring/alerts/alerts.bicep' = {
  name: 'day8Alerts'
  params: {
    location: location
    logAnalyticsWorkspaceId: observability.outputs.logAnalyticsWorkspaceId
  }
}

output acrId string = acr.outputs.acrId
output acrLoginServer string = acr.outputs.acrLoginServer
output acrName string = acr.outputs.acrName
output appInsightsConnectionString string = observability.outputs.appInsightsConnectionString
output containerAppsEnvironmentId string = containerAppsEnv.outputs.containerAppsEnvironmentId
output containerAppsEnvironmentName string = containerAppsEnv.outputs.containerAppsEnvironmentName
output keyVaultId string = keyVault.outputs.keyVaultId
output keyVaultUri string = keyVault.outputs.keyVaultUri
output location string = location
output foundryEndpoint string = core.outputs.foundryEndpoint
output foundryId string = core.outputs.foundryId
output foundryName string = core.outputs.foundryName
output openAiApiVersion string = core.outputs.openAiApiVersion
output openAiChatCapacity int = core.outputs.openAiChatCapacity
output openAiChatDeploymentName string = core.outputs.openAiChatDeploymentName
output openAiChatModelName string = core.outputs.openAiChatModelName
output openAiChatModelVersion string = core.outputs.openAiChatModelVersion
output openAiChatSkuName string = core.outputs.openAiChatSkuName
output openAiEndpoint string = core.outputs.openAiEndpoint
output openAiId string = core.outputs.openAiId
output openAiName string = core.outputs.openAiName
output postgresDatabaseName string = postgres.outputs.postgresDatabaseName
output postgresHost string = postgres.outputs.postgresHost
output postgresServerId string = postgres.outputs.postgresServerId
output postgresServerName string = postgres.outputs.postgresServerName
output postgresUser string = postgres.outputs.postgresUser
output searchEndpoint string = core.outputs.searchEndpoint
output searchIndexName string = core.outputs.searchIndexName
output searchName string = core.outputs.searchName
output searchServiceId string = core.outputs.searchServiceId
output storageAccountId string = core.outputs.storageAccountId
output storageAccountName string = core.outputs.storageAccountName
output storageAccountUrl string = core.outputs.storageAccountUrl
output storageContainerName string = core.outputs.storageContainerName
output jobsIdentityClientId string = identities.outputs.jobsIdentityClientId
output jobsIdentityPrincipalId string = identities.outputs.jobsIdentityPrincipalId
output jobsIdentityResourceId string = identities.outputs.jobsIdentityResourceId
output searchAdminIdentityClientId string = identities.outputs.searchAdminIdentityClientId
output searchAdminIdentityPrincipalId string = identities.outputs.searchAdminIdentityPrincipalId
output searchAdminIdentityResourceId string = identities.outputs.searchAdminIdentityResourceId
output workloadIdentityClientId string = identities.outputs.workloadIdentityClientId
output workloadIdentityPrincipalId string = identities.outputs.workloadIdentityPrincipalId
output workloadIdentityResourceId string = identities.outputs.workloadIdentityResourceId
output keyVaultDiagnosticsId string = keyVaultDiagnostics.outputs.diagnosticSettingId
output day8AlertsDeployment string = day8Alerts.name
