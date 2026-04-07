targetScope = 'resourceGroup'

@description('Primary region')
param location string = resourceGroup().location

@description('Container Apps environment name')
param containerAppsEnvName string

@description('Log Analytics workspace name that receives Container Apps logs')
param logAnalyticsWorkspaceName string

resource law 'Microsoft.OperationalInsights/workspaces@2023-09-01' existing = {
  name: logAnalyticsWorkspaceName
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

output containerAppsEnvironmentId string = cae.id
output containerAppsEnvironmentName string = cae.name
