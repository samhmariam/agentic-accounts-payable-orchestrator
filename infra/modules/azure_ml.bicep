targetScope = 'resourceGroup'

// Compatibility shim. Prefer infra/data/azure_ml.bicep.

param mlWorkspaceName string
param location string

@description('Resource ID of the Storage account created in the core tier')
param storageAccountId string

@description('Resource ID of the Key Vault created in the full tier')
param keyVaultId string

@description('Resource ID of the Application Insights instance created in the full tier')
param appInsightsId string

module impl '../data/azure_ml.bicep' = {
  name: '${deployment().name}-impl'
  params: {
    mlWorkspaceName: mlWorkspaceName
    location: location
    storageAccountId: storageAccountId
    keyVaultId: keyVaultId
    appInsightsId: appInsightsId
  }
}

output mlWorkspaceId string = impl.outputs.mlWorkspaceId
output mlWorkspaceName string = impl.outputs.mlWorkspaceName
output mlPrincipalId string = impl.outputs.mlPrincipalId
