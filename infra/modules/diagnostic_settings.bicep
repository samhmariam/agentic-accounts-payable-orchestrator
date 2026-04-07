targetScope = 'resourceGroup'

// Compatibility shim. Prefer infra/foundations/diagnostic_settings.bicep.

param keyVaultName string
param logAnalyticsWorkspaceName string

module impl '../foundations/diagnostic_settings.bicep' = {
  name: '${deployment().name}-impl'
  params: {
    keyVaultName: keyVaultName
    logAnalyticsWorkspaceName: logAnalyticsWorkspaceName
  }
}

output diagnosticSettingId string = impl.outputs.diagnosticSettingId
