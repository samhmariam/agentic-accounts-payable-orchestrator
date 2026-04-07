targetScope = 'resourceGroup'

// Azure AI Content Safety — provisioned for Day 7 (guardrails, PromptShield).
// Access via DefaultAzureCredential + Cognitive Services User RBAC role.

param contentSafetyName string
param location string

resource contentSafety 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  name: contentSafetyName
  location: location
  kind: 'ContentSafety'
  sku: {
    name: 'S0'
  }
  properties: {
    customSubDomainName: contentSafetyName
    disableLocalAuth: true
    publicNetworkAccess: 'Enabled'
  }
}

output contentSafetyEndpoint string = contentSafety.properties.endpoint
output contentSafetyId string = contentSafety.id
output contentSafetyName string = contentSafety.name
