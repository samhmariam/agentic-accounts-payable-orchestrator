targetScope = 'resourceGroup'

// ── Required parameters (supplied by azd from .azure/<env>/.env) ─────────────

@description('azd environment name — all resource names are derived from this value')
param envName string

@description('Azure region for all resources')
param location string = resourceGroup().location

// ── Optional parameters ───────────────────────────────────────────────────────

@description('''Notebook profile that controls which Azure resources are provisioned.
  core     (Days 3-4)  : Storage, Azure OpenAI, Azure AI Search
  standard (Days 5-7)  : core + PostgreSQL, Content Safety, Cosmos DB, ADF
  full     (Days 8-10) : standard + ACR, Key Vault, ACA environment, Log Analytics,
                         Application Insights, Azure Machine Learning
  advanced (Days 11-14): full + VNet, Private Endpoints, Private DNS, Service Bus''')
@allowed(['core', 'standard', 'full', 'advanced'])
param notebookProfile string = 'core'

@description('Entra object ID of the PostgreSQL Entra admin (required when profile is standard or above)')
param postgresAdminObjectId string = ''

@description('Entra display name or UPN of the PostgreSQL Entra admin')
param postgresAdminName string = ''

@description('Name of the Azure OpenAI chat deployment')
param openAiChatDeploymentName string = 'chat'

@description('Azure OpenAI model identifier (e.g. gpt-4o). Leave empty to skip automatic deployment creation')
param openAiChatModelName string = ''

@description('Azure OpenAI model version to pin (e.g. 2024-11-20). Leave empty to skip pinning')
param openAiChatModelVersion string = ''

@description('Azure OpenAI REST API version surfaced to notebooks as AZURE_OPENAI_API_VERSION')
param openAiApiVersion string = '2024-08-01-preview'

// ── Derived resource names ────────────────────────────────────────────────────
// All names are derived from envName — learners only need to set AZURE_ENV_NAME,
// AZURE_LOCATION, and NOTEBOOK_PROFILE.

var safeName = replace(replace(toLower(envName), '-', ''), '_', '')

var storageAccountName = take('st${safeName}', 24)
var searchName = 'aegis-srch-${take(envName, 14)}'
var openAiName = 'aegis-oai-${take(envName, 13)}'
var postgresServerName = 'aegis-pg-${take(envName, 14)}'
var postgresDatabaseName = 'aegisap'
var contentSafetyName = 'aegis-cs-${take(envName, 14)}'
var cosmosAccountName = 'aegis-cosmos-${take(envName, 11)}'
var adfName = 'aegis-adf-${take(envName, 14)}'
var acrName = take('acr${safeName}', 50)
var keyVaultName = 'aegis-kv-${take(envName, 14)}'
var logAnalyticsName = 'aegis-law-${take(envName, 13)}'
var appInsightsName = 'aegis-appi-${take(envName, 12)}'
var containerAppsEnvName = 'aegis-cae-${take(envName, 14)}'
var mlWorkspaceName = 'aegis-ml-${take(envName, 15)}'
var vnetName = 'aegis-vnet-${take(envName, 12)}'
var serviceBusName = 'aegis-sb-${take(envName, 15)}'
var workloadIdentityName = 'id-aegisap-workload'
var jobsIdentityName = 'id-aegisap-jobs'
var searchAdminIdentityName = 'id-aegisap-search-admin'

// ── Profile flags ─────────────────────────────────────────────────────────────

var isStandard = notebookProfile == 'standard' || notebookProfile == 'full' || notebookProfile == 'advanced'
var isFull = notebookProfile == 'full' || notebookProfile == 'advanced'
var isAdvanced = notebookProfile == 'advanced'

// ── Tier 1: Core (Days 3-4) ── Storage · Azure OpenAI · Azure AI Search ──────

module coreResources './core.bicep' = {
  name: '${deployment().name}-core'
  params: {
    location: location
    storageAccountName: storageAccountName
    searchName: searchName
    openAiName: openAiName
    openAiChatDeploymentName: openAiChatDeploymentName
    openAiChatModelName: openAiChatModelName
    openAiChatModelVersion: openAiChatModelVersion
    openAiApiVersion: openAiApiVersion
  }
}

// ── Tier 2: Standard (Days 5-7) ── + PostgreSQL · Content Safety · Cosmos DB · ADF

module standardResources './notebook_standard.bicep' = if (isStandard) {
  name: '${deployment().name}-standard'
  params: {
    location: location
    postgresServerName: postgresServerName
    postgresDatabaseName: postgresDatabaseName
    contentSafetyName: contentSafetyName
    cosmosAccountName: cosmosAccountName
    adfName: adfName
    postgresAdminObjectId: postgresAdminObjectId
    postgresAdminName: postgresAdminName
  }
}

// ── Tier 3: Full (Days 8-10) ── + ACR · Key Vault · ACA · Log Analytics · App Insights · Azure ML

module fullResources './notebook_full.bicep' = if (isFull) {
  name: '${deployment().name}-full'
  params: {
    location: location
    acrName: acrName
    keyVaultName: keyVaultName
    logAnalyticsName: logAnalyticsName
    appInsightsName: appInsightsName
    containerAppsEnvName: containerAppsEnvName
    mlWorkspaceName: mlWorkspaceName
    storageAccountName: storageAccountName
    workloadIdentityName: workloadIdentityName
    jobsIdentityName: jobsIdentityName
    searchAdminIdentityName: searchAdminIdentityName
  }
}

// ── Tier 4: Advanced (Days 11-14) ── + VNet · Private Endpoints · Private DNS · Service Bus

module advancedResources './notebook_advanced.bicep' = if (isAdvanced) {
  name: '${deployment().name}-advanced'
  dependsOn: [coreResources, fullResources]
  params: {
    location: location
    vnetName: vnetName
    serviceBusName: serviceBusName
    openAiName: openAiName
    storageAccountName: storageAccountName
    searchName: searchName
    keyVaultName: keyVaultName
  }
}

// ── Outputs (azd surfaces these as environment variables in .azure/<env>/.env) ─

// Core — always present
output AZURE_STORAGE_ACCOUNT_NAME string = coreResources.outputs.storageAccountName
output AZURE_STORAGE_ACCOUNT_URL string = coreResources.outputs.storageAccountUrl
output AZURE_STORAGE_CONTAINER_NAME string = coreResources.outputs.storageContainerName
output AZURE_OPENAI_ENDPOINT string = coreResources.outputs.openAiEndpoint
output AZURE_OPENAI_API_VERSION string = coreResources.outputs.openAiApiVersion
output AZURE_OPENAI_CHAT_DEPLOYMENT string = coreResources.outputs.openAiChatDeploymentName
output AZURE_SEARCH_ENDPOINT string = coreResources.outputs.searchEndpoint
output AZURE_SEARCH_INDEX_NAME string = coreResources.outputs.searchIndexName
output NOTEBOOK_PROFILE string = notebookProfile

// Standard — populated when profile is standard, full, or advanced
output AZURE_POSTGRES_HOST string = isStandard ? standardResources.outputs.AZURE_POSTGRES_HOST : ''
output AZURE_POSTGRES_DB string = isStandard ? standardResources.outputs.AZURE_POSTGRES_DB : ''
output AZURE_CONTENT_SAFETY_ENDPOINT string = isStandard ? standardResources.outputs.AZURE_CONTENT_SAFETY_ENDPOINT : ''
output AZURE_COSMOS_ENDPOINT string = isStandard ? standardResources.outputs.AZURE_COSMOS_ENDPOINT : ''

// Full — populated when profile is full or advanced
output AZURE_KEY_VAULT_URI string = isFull ? fullResources.outputs.AZURE_KEY_VAULT_URI : ''
output AZURE_ACR_LOGIN_SERVER string = isFull ? fullResources.outputs.AZURE_ACR_LOGIN_SERVER : ''
output AZURE_CONTAINER_APPS_ENVIRONMENT_ID string = isFull
  ? fullResources.outputs.AZURE_CONTAINER_APPS_ENVIRONMENT_ID
  : ''
output APPLICATIONINSIGHTS_CONNECTION_STRING string = isFull
  ? fullResources.outputs.APPLICATIONINSIGHTS_CONNECTION_STRING
  : ''
output AZURE_ML_WORKSPACE_ID string = isFull ? fullResources.outputs.AZURE_ML_WORKSPACE_ID : ''

// Advanced — populated when profile is advanced
output AZURE_VNET_ID string = isAdvanced ? advancedResources.outputs.AZURE_VNET_ID : ''
output AZURE_SERVICE_BUS_HOSTNAME string = isAdvanced ? advancedResources.outputs.AZURE_SERVICE_BUS_HOSTNAME : ''
output AZURE_SERVICE_BUS_NAMESPACE string = isAdvanced ? advancedResources.outputs.AZURE_SERVICE_BUS_NAMESPACE : ''
