targetScope = 'resourceGroup'

@description('Compatibility wrapper for the default core Day 0 template')
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

module core './core.bicep' = {
  name: 'day0Core'
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

output location string = core.outputs.location
output openAiApiVersion string = core.outputs.openAiApiVersion
output openAiChatCapacity int = core.outputs.openAiChatCapacity
output openAiChatDeploymentName string = core.outputs.openAiChatDeploymentName
output openAiChatModelName string = core.outputs.openAiChatModelName
output openAiChatModelVersion string = core.outputs.openAiChatModelVersion
output openAiChatSkuName string = core.outputs.openAiChatSkuName
output openAiEndpoint string = core.outputs.openAiEndpoint
output openAiId string = core.outputs.openAiId
output openAiName string = core.outputs.openAiName
output searchEndpoint string = core.outputs.searchEndpoint
output searchIndexName string = core.outputs.searchIndexName
output searchName string = core.outputs.searchName
output searchServiceId string = core.outputs.searchServiceId
output storageAccountId string = core.outputs.storageAccountId
output storageAccountName string = core.outputs.storageAccountName
output storageAccountUrl string = core.outputs.storageAccountUrl
output storageContainerName string = core.outputs.storageContainerName
