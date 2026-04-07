targetScope = 'resourceGroup'

// Compatibility shim. Prefer infra/data/cosmos_db.bicep.

param cosmosAccountName string
param location string

@description('Name of the NoSQL database inside the account')
param databaseName string = 'aegisap'

module impl '../data/cosmos_db.bicep' = {
  name: '${deployment().name}-impl'
  params: {
    cosmosAccountName: cosmosAccountName
    location: location
    databaseName: databaseName
  }
}

output cosmosEndpoint string = impl.outputs.cosmosEndpoint
output cosmosAccountId string = impl.outputs.cosmosAccountId
output cosmosDatabaseName string = impl.outputs.cosmosDatabaseName
