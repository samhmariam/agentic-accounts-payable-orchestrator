targetScope = 'resourceGroup'

@description('Primary region')
param location string = resourceGroup().location

@description('User-assigned managed identity name used for registry pull and Key Vault secret references')
param workloadIdentityName string = 'id-aegisap-workload'

@description('User-assigned managed identity name scaffolded for background jobs and replay workers')
param jobsIdentityName string = 'id-aegisap-jobs'

@description('User-assigned managed identity name scaffolded for Search indexing and schema administration')
param searchAdminIdentityName string = 'id-aegisap-search-admin'

resource workloadIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: workloadIdentityName
  location: location
}

resource jobsIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: jobsIdentityName
  location: location
}

resource searchAdminIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: searchAdminIdentityName
  location: location
}

output jobsIdentityClientId string = jobsIdentity.properties.clientId
output jobsIdentityPrincipalId string = jobsIdentity.properties.principalId
output jobsIdentityResourceId string = jobsIdentity.id
output searchAdminIdentityClientId string = searchAdminIdentity.properties.clientId
output searchAdminIdentityPrincipalId string = searchAdminIdentity.properties.principalId
output searchAdminIdentityResourceId string = searchAdminIdentity.id
output workloadIdentityClientId string = workloadIdentity.properties.clientId
output workloadIdentityPrincipalId string = workloadIdentity.properties.principalId
output workloadIdentityResourceId string = workloadIdentity.id
