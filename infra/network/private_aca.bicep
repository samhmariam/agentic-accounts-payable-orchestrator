// infra/network/private_aca.bicep
// VNET-injected Container Apps Environment.
// Sets internal=true so the environment has no public IP.
// Workers are reachable only from within the VNet or via APIM.

param location string
param environmentName string
param acaSubnetId string
param logAnalyticsWorkspaceId string
param logAnalyticsCustomerId string

@secure()
param logAnalyticsSharedKey string

resource acaEnvironment 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: environmentName
  location: location
  properties: {
    vnetConfiguration: {
      infrastructureSubnetId: acaSubnetId
      internal: true
    }
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalyticsCustomerId
        sharedKey: logAnalyticsSharedKey
      }
    }
    workloadProfiles: [
      {
        name: 'Consumption'
        workloadProfileType: 'Consumption'
      }
    ]
  }
}

output environmentId string = acaEnvironment.id
output environmentName string = acaEnvironment.name
output staticIp string = acaEnvironment.properties.staticIp
output defaultDomain string = acaEnvironment.properties.defaultDomain
