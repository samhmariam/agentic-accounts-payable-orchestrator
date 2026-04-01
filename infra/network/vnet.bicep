// infra/network/vnet.bicep
// Virtual Network with subnets for AegisAP private networking

param location string
param vnetName string
param vnetAddressPrefix string = '10.0.0.0/16'

@description('Subnet for Container Apps Environment infrastructure')
param acaSubnetPrefix string = '10.0.0.0/21'

@description('Subnet for Private Endpoints')
param privateEndpointSubnetPrefix string = '10.0.8.0/24'

@description('Subnet for Azure Functions')
param functionsSubnetPrefix string = '10.0.9.0/24'

resource vnet 'Microsoft.Network/virtualNetworks@2023-04-01' = {
  name: vnetName
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: [vnetAddressPrefix]
    }
    subnets: [
      {
        name: 'aca-infra'
        properties: {
          addressPrefix: acaSubnetPrefix
          delegations: []
          privateEndpointNetworkPolicies: 'Disabled'
        }
      }
      {
        name: 'private-endpoints'
        properties: {
          addressPrefix: privateEndpointSubnetPrefix
          privateEndpointNetworkPolicies: 'Disabled'
          privateLinkServiceNetworkPolicies: 'Enabled'
        }
      }
      {
        name: 'functions'
        properties: {
          addressPrefix: functionsSubnetPrefix
          delegations: [
            {
              name: 'functions-delegation'
              properties: {
                serviceName: 'Microsoft.Web/serverFarms'
              }
            }
          ]
          privateEndpointNetworkPolicies: 'Disabled'
        }
      }
    ]
  }
}

output vnetId string = vnet.id
output vnetName string = vnet.name
output acaSubnetId string = vnet.properties.subnets[0].id
output privateEndpointSubnetId string = vnet.properties.subnets[1].id
output functionsSubnetId string = vnet.properties.subnets[2].id
