targetScope = 'resourceGroup'

@description('Primary region')
param location string = resourceGroup().location

@description('PostgreSQL server name')
param postgresServerName string

@description('PostgreSQL application database name')
param postgresDatabaseName string = 'aegisap'

@description('Object ID of the PostgreSQL Microsoft Entra admin principal')
param postgresEntraAdminObjectId string = ''

@description('Name of the PostgreSQL Microsoft Entra admin principal')
param postgresEntraAdminName string = ''

@allowed([
  'User'
  'ServicePrincipal'
  'Group'
  'Unknown'
])
@description('Principal type for the PostgreSQL Microsoft Entra admin')
param postgresEntraAdminType string = 'User'

resource pg 'Microsoft.DBforPostgreSQL/flexibleServers@2024-08-01' = {
  name: postgresServerName
  location: location
  sku: {
    name: 'Standard_B1ms'
    tier: 'Burstable'
  }
  properties: {
    authConfig: {
      activeDirectoryAuth: 'Enabled'
      passwordAuth: 'Disabled'
      tenantId: subscription().tenantId
    }
    network: {
      publicNetworkAccess: 'Enabled'
    }
    storage: {
      storageSizeGB: 128
    }
    version: '16'
  }
}

resource pgAdmin 'Microsoft.DBforPostgreSQL/flexibleServers/administrators@2024-08-01' = if (!empty(postgresEntraAdminObjectId)) {
  parent: pg
  name: postgresEntraAdminObjectId
  properties: {
    principalName: postgresEntraAdminName
    principalType: postgresEntraAdminType
    tenantId: subscription().tenantId
  }
}

resource pgDb 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2024-08-01' = {
  parent: pg
  name: postgresDatabaseName
  properties: {
    charset: 'UTF8'
    collation: 'en_US.utf8'
  }
}

output postgresDatabaseName string = pgDb.name
output postgresHost string = pg.properties.fullyQualifiedDomainName
output postgresServerId string = pg.id
output postgresServerName string = pg.name
output postgresUser string = postgresEntraAdminName
