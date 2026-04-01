// infra/modules/cosmos_db.bicep
// Azure Cosmos DB for NoSQL — stub for Day 6 (vendor master, invoice status store).
// Uses serverless SKU and Managed Identity authentication (no connection strings).

param cosmosAccountName string
param location string

@description('Name of the NoSQL database inside the account')
param databaseName string = 'aegisap'

resource cosmosAccount 'Microsoft.DocumentDB/databaseAccounts@2024-05-15' = {
  name: cosmosAccountName
  location: location
  kind: 'GlobalDocumentDB'
  properties: {
    databaseAccountOfferType: 'Standard'
    disableLocalAuth: true
    capabilities: [
      { name: 'EnableServerless' }
    ]
    consistencyPolicy: {
      defaultConsistencyLevel: 'Session'
    }
    locations: [
      {
        locationName: location
        failoverPriority: 0
        isZoneRedundant: false
      }
    ]
    publicNetworkAccess: 'Enabled'
  }
}

resource cosmosDatabase 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2024-05-15' = {
  parent: cosmosAccount
  name: databaseName
  properties: {
    resource: {
      id: databaseName
    }
  }
}

output cosmosEndpoint string = cosmosAccount.properties.documentEndpoint
output cosmosAccountId string = cosmosAccount.id
output cosmosDatabaseName string = cosmosDatabase.name
