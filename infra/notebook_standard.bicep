targetScope = 'resourceGroup'

// Tier 2 resources: Days 5-7
// PostgreSQL · Content Safety · Cosmos DB · Azure Data Factory

param location string
param postgresServerName string
param postgresDatabaseName string
param contentSafetyName string
param cosmosAccountName string
param adfName string

@description('Entra object ID of the PostgreSQL Entra admin. Leave empty to skip admin registration')
param postgresAdminObjectId string = ''

@description('Entra UPN or display name of the PostgreSQL Entra admin')
param postgresAdminName string = ''

// ── PostgreSQL Flexible Server (Days 5+) ─────────────────────────────────────

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

resource pgAdmin 'Microsoft.DBforPostgreSQL/flexibleServers/administrators@2024-08-01' = if (!empty(postgresAdminObjectId)) {
  parent: pg
  name: postgresAdminObjectId
  properties: {
    principalName: postgresAdminName
    principalType: 'User'
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

// ── Content Safety (Day 7) ────────────────────────────────────────────────────

module contentSafetyMod './modules/content_safety.bicep' = {
  name: '${deployment().name}-cs'
  params: {
    contentSafetyName: contentSafetyName
    location: location
  }
}

// ── Cosmos DB for NoSQL (Day 6 — stub) ───────────────────────────────────────

module cosmosMod './modules/cosmos_db.bicep' = {
  name: '${deployment().name}-cosmos'
  params: {
    cosmosAccountName: cosmosAccountName
    location: location
  }
}

// ── Azure Data Factory (Day 6 — stub) ────────────────────────────────────────

module adfMod './modules/adf.bicep' = {
  name: '${deployment().name}-adf'
  params: {
    adfName: adfName
    location: location
  }
}

// ── Outputs ───────────────────────────────────────────────────────────────────

output AZURE_POSTGRES_HOST string = pg.properties.fullyQualifiedDomainName
output AZURE_POSTGRES_DB string = pgDb.name
output AZURE_CONTENT_SAFETY_ENDPOINT string = contentSafetyMod.outputs.contentSafetyEndpoint
output AZURE_COSMOS_ENDPOINT string = cosmosMod.outputs.cosmosEndpoint
output AZURE_ADF_PRINCIPAL_ID string = adfMod.outputs.adfPrincipalId
