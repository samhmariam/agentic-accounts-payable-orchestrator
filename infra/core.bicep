targetScope = 'resourceGroup'

@description('Primary region')
param location string = resourceGroup().location

@description('Storage account name')
param storageAccountName string

@description('Blob container name for source documents')
param storageContainerName string = 'documents'

@description('Search service name')
param searchName string

@description('Starter search index name for Day 0')
param searchIndexName string = 'documents'

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
output searchEndpoint string = srch.properties.endpoint
output searchIndexName string = searchIndexName
output searchName string = srch.name
output searchServiceId string = srch.id
output storageAccountId string = st.id
output storageAccountName string = st.name
output storageAccountUrl string = st.properties.primaryEndpoints.blob
output storageContainerName string = stContainer.name
