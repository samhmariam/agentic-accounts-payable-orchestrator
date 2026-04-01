// infra/network/private_endpoints.bicep
// Private Endpoints for all AegisAP AI services.
// Each PE brings the service into the VNet via a private NIC.
// A DNS zone group registers the private IP in the corresponding DNS zone.

param location string
param privateEndpointSubnetId string

param openAiAccountId string
param openAiAccountName string

param searchServiceId string
param searchServiceName string

param storageAccountId string
param storageAccountName string

param keyVaultId string
param keyVaultName string

// DNS zone IDs (outputs from private_dns.bicep)
param openAiDnsZoneId string
param searchDnsZoneId string
param blobDnsZoneId string
param keyVaultDnsZoneId string

// ── Azure OpenAI ───────────────────────────────────────────────────────────
resource openAiPe 'Microsoft.Network/privateEndpoints@2023-04-01' = {
  name: '${openAiAccountName}-pe'
  location: location
  properties: {
    subnet: { id: privateEndpointSubnetId }
    privateLinkServiceConnections: [
      {
        name: '${openAiAccountName}-plsc'
        properties: {
          privateLinkServiceId: openAiAccountId
          groupIds: ['account']
        }
      }
    ]
  }
}

resource openAiDnsGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2023-04-01' = {
  parent: openAiPe
  name: 'dns-group'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'openai-config'
        properties: { privateDnsZoneId: openAiDnsZoneId }
      }
    ]
  }
}

// ── Azure AI Search ────────────────────────────────────────────────────────
resource searchPe 'Microsoft.Network/privateEndpoints@2023-04-01' = {
  name: '${searchServiceName}-pe'
  location: location
  properties: {
    subnet: { id: privateEndpointSubnetId }
    privateLinkServiceConnections: [
      {
        name: '${searchServiceName}-plsc'
        properties: {
          privateLinkServiceId: searchServiceId
          groupIds: ['searchService']
        }
      }
    ]
  }
}

resource searchDnsGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2023-04-01' = {
  parent: searchPe
  name: 'dns-group'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'search-config'
        properties: { privateDnsZoneId: searchDnsZoneId }
      }
    ]
  }
}

// ── Azure Storage (blob) ───────────────────────────────────────────────────
resource storagePe 'Microsoft.Network/privateEndpoints@2023-04-01' = {
  name: '${storageAccountName}-pe'
  location: location
  properties: {
    subnet: { id: privateEndpointSubnetId }
    privateLinkServiceConnections: [
      {
        name: '${storageAccountName}-plsc'
        properties: {
          privateLinkServiceId: storageAccountId
          groupIds: ['blob']
        }
      }
    ]
  }
}

resource storageDnsGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2023-04-01' = {
  parent: storagePe
  name: 'dns-group'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'blob-config'
        properties: { privateDnsZoneId: blobDnsZoneId }
      }
    ]
  }
}

// ── Azure Key Vault ────────────────────────────────────────────────────────
resource keyVaultPe 'Microsoft.Network/privateEndpoints@2023-04-01' = {
  name: '${keyVaultName}-pe'
  location: location
  properties: {
    subnet: { id: privateEndpointSubnetId }
    privateLinkServiceConnections: [
      {
        name: '${keyVaultName}-plsc'
        properties: {
          privateLinkServiceId: keyVaultId
          groupIds: ['vault']
        }
      }
    ]
  }
}

resource keyVaultDnsGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2023-04-01' = {
  parent: keyVaultPe
  name: 'dns-group'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'kv-config'
        properties: { privateDnsZoneId: keyVaultDnsZoneId }
      }
    ]
  }
}
