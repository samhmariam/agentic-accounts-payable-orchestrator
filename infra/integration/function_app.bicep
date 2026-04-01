// infra/integration/function_app.bicep
// Azure Functions (Flex Consumption) for LOB boundary.
// Uses Managed Identity — no connection strings in app settings.
// VNET-integrated via functions subnet.

param location string
param appName string
param storageAccountName string
param appServicePlanName string
param functionsSubnetId string
param keyVaultName string
param serviceBusNamespaceName string
param workerContainerAppFqdn string
param appClientId string

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' existing = {
  name: storageAccountName
}

resource appServicePlan 'Microsoft.Web/serverfarms@2022-03-01' = {
  name: appServicePlanName
  location: location
  sku: {
    name: 'FC1'
    tier: 'FlexConsumption'
  }
  kind: 'functionapp'
  properties: {
    reserved: true // Linux
  }
}

resource functionApp 'Microsoft.Web/sites@2022-03-01' = {
  name: appName
  location: location
  kind: 'functionapp,linux'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: appServicePlan.id
    virtualNetworkSubnetId: functionsSubnetId
    vnetContentShareEnabled: false
    httpsOnly: true
    siteConfig: {
      pythonVersion: '3.11'
      appSettings: [
        {
          name: 'AzureWebJobsStorage__accountName'
          value: storageAccountName
        }
        {
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~4'
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'python'
        }
        {
          name: 'AZURE_CLIENT_ID'
          value: appClientId
        }
        {
          name: 'AEGISAP_WORKER_URL'
          value: 'https://${workerContainerAppFqdn}'
        }
        {
          name: 'KEY_VAULT_NAME'
          value: keyVaultName
        }
        {
          name: 'AZURE_SERVICE_BUS_NAMESPACE'
          value: serviceBusNamespaceName
        }
      ]
      ftpsState: 'Disabled'
      minTlsVersion: '1.2'
    }
  }
}

// Grant Functions MI: Storage Blob Data Contributor on the storage account
resource storageBlobRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(storageAccount.id, functionApp.id, 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')
  scope: storageAccount
  properties: {
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
    )
    principalId: functionApp.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

output functionAppId string = functionApp.id
output functionAppName string = functionApp.name
output functionAppPrincipalId string = functionApp.identity.principalId
output functionAppDefaultHostname string = functionApp.properties.defaultHostName
