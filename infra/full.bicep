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

@description('Azure OpenAI account name')
param openAiName string

@description('Azure OpenAI data-plane API version exported into the local environment')
param openAiApiVersion string = '2024-08-01-preview'

@description('Azure OpenAI chat deployment name exported into the local environment')
param openAiChatDeploymentName string

@description('Optional Azure OpenAI chat model name for automatic deployment creation')
param openAiChatModelName string = ''

@description('Optional Azure OpenAI chat model version for automatic deployment creation')
param openAiChatModelVersion string = ''

@description('Optional Azure OpenAI deployment SKU name')
param openAiChatSkuName string = 'Standard'

@description('Optional Azure OpenAI deployment capacity')
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

resource st 'Microsoft.Storage/storageAccounts@2025-06-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    allowBlobPublicAccess: false
    allowSharedKeyAccess: false
    defaultToOAuthAuthentication: true
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
  }
}

resource stBlob 'Microsoft.Storage/storageAccounts/blobServices@2025-06-01' = {
  parent: st
  name: 'default'
}

resource stContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2025-06-01' = {
  parent: stBlob
  name: storageContainerName
  properties: {
    publicAccess: 'None'
  }
}

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

resource appi 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: law.id
  }
}

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

resource srch 'Microsoft.Search/searchServices@2025-05-01' = {
  name: searchName
  location: location
  sku: {
    name: 'basic'
  }
  properties: {
    disableLocalAuth: true
    hostingMode: 'Default'
    partitionCount: 1
    publicNetworkAccess: 'enabled'
    replicaCount: 1
  }
}

resource pg 'Microsoft.DBforPostgreSQL/flexibleServers@2024-08-01' = {
  name: postgresServerName
  location: location
  sku: {
    name: 'Standard_B1ms'
    tier: 'Burstable'
  }
  properties: {
    authConfig: {
      activeDirectoryAuth: 'Enabled'
      passwordAuth: 'Disabled'
      tenantId: subscription().tenantId
    }
    network: {
      publicNetworkAccess: 'Enabled'
    }
    storage: {
      storageSizeGB: 128
    }
    version: '16'
  }
}

resource pgAdmin 'Microsoft.DBforPostgreSQL/flexibleServers/administrators@2024-08-01' = {
  parent: pg
  name: postgresEntraAdminObjectId
  properties: {
    principalName: postgresEntraAdminName
    principalType: postgresEntraAdminType
    tenantId: subscription().tenantId
  }
}

resource pgDb 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2024-08-01' = {
  parent: pg
  name: postgresDatabaseName
  properties: {
    charset: 'UTF8'
    collation: 'en_US.utf8'
  }
}

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

module keyVaultDiagnostics './modules/diagnostic_settings.bicep' = {
  name: 'keyVaultDiagnostics'
  params: {
    keyVaultName: kv.name
    logAnalyticsWorkspaceName: law.name
  }
}

resource aoai 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  name: openAiName
  location: location
  kind: 'OpenAI'
  sku: {
    name: 'S0'
  }
  properties: {
    customSubDomainName: openAiName
    disableLocalAuth: true
    publicNetworkAccess: 'Enabled'
  }
}

output acrId string = acr.id
output acrLoginServer string = acr.properties.loginServer
output acrName string = acr.name
output appInsightsConnectionString string = appi.properties.ConnectionString
output containerAppsEnvironmentId string = cae.id
output containerAppsEnvironmentName string = cae.name
output keyVaultId string = kv.id
output keyVaultUri string = kv.properties.vaultUri
output location string = location
output openAiApiVersion string = openAiApiVersion
output openAiChatCapacity int = openAiChatCapacity
output openAiChatDeploymentName string = openAiChatDeploymentName
output openAiChatModelName string = openAiChatModelName
output openAiChatModelVersion string = openAiChatModelVersion
output openAiChatSkuName string = openAiChatSkuName
output openAiEndpoint string = 'https://${openAiName}.openai.azure.com/'
output openAiId string = aoai.id
output openAiName string = aoai.name
output postgresDatabaseName string = pgDb.name
output postgresHost string = pg.properties.fullyQualifiedDomainName
output postgresServerId string = pg.id
output postgresServerName string = pg.name
output postgresUser string = postgresEntraAdminName
output searchEndpoint string = srch.properties.endpoint
output searchIndexName string = searchIndexName
output searchName string = srch.name
output searchServiceId string = srch.id
output storageAccountId string = st.id
output storageAccountName string = st.name
output storageAccountUrl string = st.properties.primaryEndpoints.blob
output storageContainerName string = stContainer.name
output jobsIdentityClientId string = jobsIdentity.properties.clientId
output jobsIdentityPrincipalId string = jobsIdentity.properties.principalId
output jobsIdentityResourceId string = jobsIdentity.id
output searchAdminIdentityClientId string = searchAdminIdentity.properties.clientId
output searchAdminIdentityPrincipalId string = searchAdminIdentity.properties.principalId
output searchAdminIdentityResourceId string = searchAdminIdentity.id
output workloadIdentityClientId string = workloadIdentity.properties.clientId
output workloadIdentityPrincipalId string = workloadIdentity.properties.principalId
output workloadIdentityResourceId string = workloadIdentity.id
output keyVaultDiagnosticsId string = keyVaultDiagnostics.outputs.diagnosticSettingId
