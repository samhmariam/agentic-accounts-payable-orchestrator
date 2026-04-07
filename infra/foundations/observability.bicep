targetScope = 'resourceGroup'

@description('Primary region')
param location string = resourceGroup().location

@description('Log Analytics workspace name')
param logAnalyticsName string

@description('Application Insights name')
param appInsightsName string

resource law 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: logAnalyticsName
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

resource appi 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: law.id
  }
}

output appInsightsConnectionString string = appi.properties.ConnectionString
output appInsightsId string = appi.id
output appInsightsName string = appi.name
output logAnalyticsWorkspaceId string = law.id
output logAnalyticsWorkspaceName string = law.name
