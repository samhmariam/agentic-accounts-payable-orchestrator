// infra/network/private_dns.bicep
// Private DNS zones for all AegisAP Azure services.
// Zones must be linked to the VNet so that service hostnames
// resolve to private IPs inside the VNet (split-horizon DNS).

param vnetId string
param vnetName string

var dnsZones = [
  'privatelink.openai.azure.com'
  'privatelink.search.windows.net'
  'privatelink.blob.core.windows.net'
  'privatelink.postgres.database.azure.com'
  'privatelink.vaultcore.azure.net'
]

resource privateDnsZones 'Microsoft.Network/privateDnsZones@2020-06-01' = [
  for zone in dnsZones: {
    name: zone
    location: 'global'
  }
]

resource dnsZoneLinks 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2020-06-01' = [
  for (zone, i) in dnsZones: {
    parent: privateDnsZones[i]
    name: '${vnetName}-link'
    location: 'global'
    properties: {
      virtualNetwork: { id: vnetId }
      registrationEnabled: false
    }
  }
]

output openAiDnsZoneId string = privateDnsZones[0].id
output searchDnsZoneId string = privateDnsZones[1].id
output blobDnsZoneId string = privateDnsZones[2].id
output postgresDnsZoneId string = privateDnsZones[3].id
output keyVaultDnsZoneId string = privateDnsZones[4].id
