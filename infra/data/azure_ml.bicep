targetScope = 'resourceGroup'

// Azure Machine Learning Workspace — stub for Days 8-10 (MLflow tracking, eval runs).
// Requires storage, key vault, and application insights as associated resources.
// All three must already exist; their resource IDs are passed as parameters.

param mlWorkspaceName string
param location string

@description('Resource ID of the Storage account created in the core tier')
param storageAccountId string

@description('Resource ID of the Key Vault created in the full tier')
param keyVaultId string

@description('Resource ID of the Application Insights instance created in the full tier')
param appInsightsId string

resource mlWorkspace 'Microsoft.MachineLearningServices/workspaces@2024-04-01' = {
  name: mlWorkspaceName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  sku: {
    name: 'Basic'
    tier: 'Basic'
  }
  properties: {
    storageAccount: storageAccountId
    keyVault: keyVaultId
    applicationInsights: appInsightsId
    publicNetworkAccess: 'Enabled'
    v1LegacyMode: false
  }
}

output mlWorkspaceId string = mlWorkspace.id
output mlWorkspaceName string = mlWorkspace.name
output mlPrincipalId string = mlWorkspace.identity.principalId
