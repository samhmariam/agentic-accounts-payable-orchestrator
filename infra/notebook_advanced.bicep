targetScope = 'resourceGroup'

// Tier 4 resources: Days 11-14
// VNet · Private DNS Zones · Private Endpoints · Service Bus
//
// NOTE: Private endpoints for AI services are added here, but the AI service
// resources themselves retain publicNetworkAccess: 'Enabled' from the core tier.
// In production, disable public access after private endpoints are confirmed
// healthy. This is intentional for a training environment to allow notebook
// connectivity from outside the VNet during learning exercises.

param location string
param vnetName string
param serviceBusName string

// Names of resources created by earlier tiers — used to build existing references
// so private endpoint target IDs can be resolved without module output wiring.
param openAiName string
param storageAccountName string
param searchName string
param keyVaultName string

// ── References to resources provisioned by earlier tiers ─────────────────────

resource openAi 'Microsoft.CognitiveServices/accounts@2024-10-01' existing = {
  name: openAiName
}

resource storageAccount 'Microsoft.Storage/storageAccounts@2025-06-01' existing = {
  name: storageAccountName
}

resource searchService 'Microsoft.Search/searchServices@2025-05-01' existing = {
  name: searchName
}

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' existing = {
  name: keyVaultName
}

// ── VNet (Day 12) ─────────────────────────────────────────────────────────────

module vnet './network/vnet.bicep' = {
  name: '${deployment().name}-vnet'
  params: {
    location: location
    vnetName: vnetName
  }
}

// ── Private DNS Zones + VNet links (Day 12) ───────────────────────────────────

module privateDns './network/private_dns.bicep' = {
  name: '${deployment().name}-dns'
  params: {
    vnetId: vnet.outputs.vnetId
    vnetName: vnetName
  }
}

// ── Private Endpoints for AI services (Day 12) ───────────────────────────────

module privateEndpoints './network/private_endpoints.bicep' = {
  name: '${deployment().name}-pe'
  params: {
    location: location
    privateEndpointSubnetId: vnet.outputs.privateEndpointSubnetId
    openAiAccountId: openAi.id
    openAiAccountName: openAiName
    searchServiceId: searchService.id
    searchServiceName: searchName
    storageAccountId: storageAccount.id
    storageAccountName: storageAccountName
    keyVaultId: keyVault.id
    keyVaultName: keyVaultName
    openAiDnsZoneId: privateDns.outputs.openAiDnsZoneId
    searchDnsZoneId: privateDns.outputs.searchDnsZoneId
    blobDnsZoneId: privateDns.outputs.blobDnsZoneId
    keyVaultDnsZoneId: privateDns.outputs.keyVaultDnsZoneId
  }
}

// ── Service Bus (Day 13) ──────────────────────────────────────────────────────
// Standard SKU with public network access is sufficient for training exercises.
// The Day 13 focus is on the integration pattern (Functions → Service Bus → ACA),
// not on private networking of the bus itself.

resource serviceBusNamespace 'Microsoft.ServiceBus/namespaces@2022-10-01-preview' = {
  name: serviceBusName
  location: location
  sku: {
    name: 'Standard'
    tier: 'Standard'
  }
  properties: {
    disableLocalAuth: true
    minimumTlsVersion: '1.2'
  }
}

resource invoiceQueue 'Microsoft.ServiceBus/namespaces/queues@2022-10-01-preview' = {
  parent: serviceBusNamespace
  name: 'invoice-submissions'
  properties: {
    maxDeliveryCount: 5
    lockDuration: 'PT2M'
    deadLetteringOnMessageExpiration: true
    defaultMessageTimeToLive: 'P1D'
  }
}

resource invoiceReplyQueue 'Microsoft.ServiceBus/namespaces/queues@2022-10-01-preview' = {
  parent: serviceBusNamespace
  name: 'invoice-results'
  properties: {
    maxDeliveryCount: 3
    lockDuration: 'PT1M'
    deadLetteringOnMessageExpiration: true
    defaultMessageTimeToLive: 'P1D'
  }
}

// ── Outputs ───────────────────────────────────────────────────────────────────

output AZURE_VNET_ID string = vnet.outputs.vnetId
output AZURE_VNET_NAME string = vnetName
output AZURE_PRIVATE_ENDPOINT_SUBNET_ID string = vnet.outputs.privateEndpointSubnetId
output AZURE_SERVICE_BUS_HOSTNAME string = '${serviceBusNamespace.name}.servicebus.windows.net'
output AZURE_SERVICE_BUS_NAMESPACE string = serviceBusNamespace.name
