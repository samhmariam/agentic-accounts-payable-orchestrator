targetScope = 'resourceGroup'

// Compatibility shim. Prefer infra/data/adf.bicep.

param adfName string
param location string

module impl '../data/adf.bicep' = {
  name: '${deployment().name}-impl'
  params: {
    adfName: adfName
    location: location
  }
}

output adfId string = impl.outputs.adfId
output adfName string = impl.outputs.adfName
output adfPrincipalId string = impl.outputs.adfPrincipalId
