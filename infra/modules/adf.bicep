// infra/modules/adf.bicep
// Azure Data Factory — stub for Day 6 (landing / curated / processed zone pipeline).
// Uses system-assigned Managed Identity; no connection strings.

param adfName string
param location string

resource dataFactory 'Microsoft.DataFactory/factories@2018-06-01' = {
  name: adfName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    publicNetworkAccess: 'Enabled'
  }
}

output adfId string = dataFactory.id
output adfName string = dataFactory.name
output adfPrincipalId string = dataFactory.identity.principalId
