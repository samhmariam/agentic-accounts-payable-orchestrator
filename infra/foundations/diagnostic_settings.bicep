targetScope = 'resourceGroup'

param keyVaultName string
param logAnalyticsWorkspaceName string

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' existing = {
  name: keyVaultName
}

resource workspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' existing = {
  name: logAnalyticsWorkspaceName
}

resource keyVaultDiagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: '${keyVaultName}-audit'
  scope: keyVault
  properties: {
    workspaceId: workspace.id
    logs: [
      {
        category: 'AuditEvent'
        enabled: true
      }
    ]
    metrics: []
  }
}

output diagnosticSettingId string = keyVaultDiagnostics.id
