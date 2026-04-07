targetScope = 'resourceGroup'

param openAiName string
param searchName string
param storageAccountName string
param keyVaultName string
param acrName string

@description('Optional: Content Safety account name for Cognitive Services User role assignment')
param contentSafetyName string = ''

param developerPrincipalId string = ''
param developerPrincipalType string = 'User'
param pullIdentityPrincipalId string = ''
param jobsIdentityPrincipalId string = ''
param searchAdminIdentityPrincipalId string = ''
param runtimeApiPrincipalId string = ''

param cognitiveServicesOpenAiUserRoleDefinitionId string
param searchIndexDataReaderRoleDefinitionId string
param searchIndexDataContributorRoleDefinitionId string
param searchServiceContributorRoleDefinitionId string
param storageBlobDataReaderRoleDefinitionId string
param storageBlobDataContributorRoleDefinitionId string
param keyVaultUserRoleId string
param acrPullRoleDefinitionId string

@description('Cognitive Services User role — grants read access to Content Safety and other Cognitive Services endpoints. Defaults to the well-known built-in role ID.')
param cognitiveServicesUserRoleDefinitionId string = subscriptionResourceId(
  'Microsoft.Authorization/roleDefinitions',
  'a97b65f3-24c7-4388-baec-2e87135dc908'
)

resource openAi 'Microsoft.CognitiveServices/accounts@2024-10-01' existing = {
  name: openAiName
}

resource searchService 'Microsoft.Search/searchServices@2025-05-01' existing = {
  name: searchName
}

resource storageAccount 'Microsoft.Storage/storageAccounts@2025-06-01' existing = {
  name: storageAccountName
}

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' existing = {
  name: keyVaultName
}

resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' existing = {
  name: acrName
}

resource developerFoundryAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(developerPrincipalId)) {
  name: guid(openAi.id, developerPrincipalId, cognitiveServicesUserRoleDefinitionId)
  scope: openAi
  properties: {
    principalId: developerPrincipalId
    principalType: developerPrincipalType
    roleDefinitionId: cognitiveServicesUserRoleDefinitionId
  }
}

resource developerSearchServiceAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(developerPrincipalId)) {
  name: guid(searchService.id, developerPrincipalId, searchServiceContributorRoleDefinitionId)
  scope: searchService
  properties: {
    principalId: developerPrincipalId
    principalType: developerPrincipalType
    roleDefinitionId: searchServiceContributorRoleDefinitionId
  }
}

resource developerSearchIndexAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(developerPrincipalId)) {
  name: guid(searchService.id, developerPrincipalId, searchIndexDataContributorRoleDefinitionId)
  scope: searchService
  properties: {
    principalId: developerPrincipalId
    principalType: developerPrincipalType
    roleDefinitionId: searchIndexDataContributorRoleDefinitionId
  }
}

resource developerStorageAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(developerPrincipalId)) {
  name: guid(storageAccount.id, developerPrincipalId, storageBlobDataContributorRoleDefinitionId)
  scope: storageAccount
  properties: {
    principalId: developerPrincipalId
    principalType: developerPrincipalType
    roleDefinitionId: storageBlobDataContributorRoleDefinitionId
  }
}

resource developerKeyVaultAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(developerPrincipalId)) {
  name: guid(keyVault.id, developerPrincipalId, keyVaultUserRoleId)
  scope: keyVault
  properties: {
    principalId: developerPrincipalId
    principalType: developerPrincipalType
    roleDefinitionId: keyVaultUserRoleId
  }
}

resource pullIdentityKeyVaultAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(pullIdentityPrincipalId)) {
  name: guid(keyVault.id, pullIdentityPrincipalId, keyVaultUserRoleId)
  scope: keyVault
  properties: {
    principalId: pullIdentityPrincipalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: keyVaultUserRoleId
  }
}

resource pullIdentityAcrAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(pullIdentityPrincipalId)) {
  name: guid(acr.id, pullIdentityPrincipalId, acrPullRoleDefinitionId)
  scope: acr
  properties: {
    principalId: pullIdentityPrincipalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: acrPullRoleDefinitionId
  }
}

resource jobsStorageAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(jobsIdentityPrincipalId)) {
  name: guid(storageAccount.id, jobsIdentityPrincipalId, storageBlobDataReaderRoleDefinitionId)
  scope: storageAccount
  properties: {
    principalId: jobsIdentityPrincipalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: storageBlobDataReaderRoleDefinitionId
  }
}

resource searchAdminServiceAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(searchAdminIdentityPrincipalId)) {
  name: guid(searchService.id, searchAdminIdentityPrincipalId, searchServiceContributorRoleDefinitionId)
  scope: searchService
  properties: {
    principalId: searchAdminIdentityPrincipalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: searchServiceContributorRoleDefinitionId
  }
}

resource searchAdminIndexAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(searchAdminIdentityPrincipalId)) {
  name: guid(searchService.id, searchAdminIdentityPrincipalId, searchIndexDataContributorRoleDefinitionId)
  scope: searchService
  properties: {
    principalId: searchAdminIdentityPrincipalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: searchIndexDataContributorRoleDefinitionId
  }
}

resource runtimeOpenAiAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(runtimeApiPrincipalId)) {
  name: guid(openAi.id, runtimeApiPrincipalId, cognitiveServicesOpenAiUserRoleDefinitionId)
  scope: openAi
  properties: {
    principalId: runtimeApiPrincipalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: cognitiveServicesOpenAiUserRoleDefinitionId
  }
}

resource runtimeSearchAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(runtimeApiPrincipalId)) {
  name: guid(searchService.id, runtimeApiPrincipalId, searchIndexDataReaderRoleDefinitionId)
  scope: searchService
  properties: {
    principalId: runtimeApiPrincipalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: searchIndexDataReaderRoleDefinitionId
  }
}

resource runtimeStorageAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(runtimeApiPrincipalId)) {
  name: guid(storageAccount.id, runtimeApiPrincipalId, storageBlobDataReaderRoleDefinitionId)
  scope: storageAccount
  properties: {
    principalId: runtimeApiPrincipalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: storageBlobDataReaderRoleDefinitionId
  }
}

resource runtimeKeyVaultAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(runtimeApiPrincipalId)) {
  name: guid(keyVault.id, runtimeApiPrincipalId, keyVaultUserRoleId)
  scope: keyVault
  properties: {
    principalId: runtimeApiPrincipalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: keyVaultUserRoleId
  }
}

// ── Content Safety (Day 7) ────────────────────────────────────────────────────

resource contentSafety 'Microsoft.CognitiveServices/accounts@2024-10-01' existing = if (!empty(contentSafetyName)) {
  name: !empty(contentSafetyName) ? contentSafetyName : 'placeholder'
}

resource developerContentSafetyAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(developerPrincipalId) && !empty(contentSafetyName)) {
  name: guid(contentSafety.id, developerPrincipalId, cognitiveServicesUserRoleDefinitionId)
  scope: contentSafety
  properties: {
    principalId: developerPrincipalId
    principalType: developerPrincipalType
    roleDefinitionId: cognitiveServicesUserRoleDefinitionId
  }
}
