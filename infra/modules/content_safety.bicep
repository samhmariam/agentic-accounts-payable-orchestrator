targetScope = 'resourceGroup'

// Compatibility shim. Prefer infra/data/content_safety.bicep.

param contentSafetyName string
param location string

module impl '../data/content_safety.bicep' = {
  name: '${deployment().name}-impl'
  params: {
    contentSafetyName: contentSafetyName
    location: location
  }
}

output contentSafetyEndpoint string = impl.outputs.contentSafetyEndpoint
output contentSafetyId string = impl.outputs.contentSafetyId
output contentSafetyName string = impl.outputs.contentSafetyName
