targetScope = 'resourceGroup'

@description('Primary region')
param location string = resourceGroup().location

@description('Search service name')
param searchName string

@description('Starter search index name surfaced into local tooling')
param searchIndexName string = 'documents'

resource srch 'Microsoft.Search/searchServices@2025-05-01' = {
  name: searchName
  location: location
  sku: {
    name: 'free'
  }
  properties: {
    disableLocalAuth: true
    hostingMode: 'Default'
    partitionCount: 1
    publicNetworkAccess: 'enabled'
    replicaCount: 1
  }
}

output searchEndpoint string = srch.properties.endpoint
output searchIndexName string = searchIndexName
output searchName string = srch.name
output searchServiceId string = srch.id
