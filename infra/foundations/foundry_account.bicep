targetScope = 'resourceGroup'

@description('Primary region')
param location string = resourceGroup().location

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

resource foundry 'Microsoft.CognitiveServices/accounts@2025-06-01' = {
  name: openAiName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  kind: 'AIServices'
  sku: {
    name: 'S0'
  }
  properties: {
    allowProjectManagement: true
    customSubDomainName: openAiName
    disableLocalAuth: true
    publicNetworkAccess: 'Enabled'
  }
}

output openAiApiVersion string = openAiApiVersion
output openAiChatCapacity int = openAiChatCapacity
output openAiChatDeploymentName string = openAiChatDeploymentName
output openAiChatModelName string = openAiChatModelName
output openAiChatModelVersion string = openAiChatModelVersion
output openAiChatSkuName string = openAiChatSkuName
output foundryEndpoint string = 'https://${openAiName}.services.ai.azure.com/'
output foundryId string = foundry.id
output foundryName string = foundry.name
output openAiEndpoint string = 'https://${openAiName}.openai.azure.com/'
output openAiId string = foundry.id
output openAiName string = foundry.name
