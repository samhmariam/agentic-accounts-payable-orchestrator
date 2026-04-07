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

module storage './foundations/storage.bicep' = {
  name: '${deployment().name}-storage'
  params: {
    location: location
    storageAccountName: storageAccountName
    storageContainerName: storageContainerName
  }
}

module search './foundations/search_service.bicep' = {
  name: '${deployment().name}-search'
  params: {
    location: location
    searchName: searchName
    searchIndexName: searchIndexName
  }
}

module foundry './foundations/foundry_account.bicep' = {
  name: '${deployment().name}-foundry'
  params: {
    location: location
    openAiName: openAiName
    openAiApiVersion: openAiApiVersion
    openAiChatDeploymentName: openAiChatDeploymentName
    openAiChatModelName: openAiChatModelName
    openAiChatModelVersion: openAiChatModelVersion
    openAiChatSkuName: openAiChatSkuName
    openAiChatCapacity: openAiChatCapacity
  }
}

output location string = location
output foundryEndpoint string = foundry.outputs.foundryEndpoint
output foundryId string = foundry.outputs.foundryId
output foundryName string = foundry.outputs.foundryName
output openAiApiVersion string = foundry.outputs.openAiApiVersion
output openAiChatCapacity int = foundry.outputs.openAiChatCapacity
output openAiChatDeploymentName string = foundry.outputs.openAiChatDeploymentName
output openAiChatModelName string = foundry.outputs.openAiChatModelName
output openAiChatModelVersion string = foundry.outputs.openAiChatModelVersion
output openAiChatSkuName string = foundry.outputs.openAiChatSkuName
output openAiEndpoint string = foundry.outputs.openAiEndpoint
output openAiId string = foundry.outputs.openAiId
output openAiName string = foundry.outputs.openAiName
output searchEndpoint string = search.outputs.searchEndpoint
output searchIndexName string = search.outputs.searchIndexName
output searchName string = search.outputs.searchName
output searchServiceId string = search.outputs.searchServiceId
output storageAccountId string = storage.outputs.storageAccountId
output storageAccountName string = storage.outputs.storageAccountName
output storageAccountUrl string = storage.outputs.storageAccountUrl
output storageContainerName string = storage.outputs.storageContainerName
