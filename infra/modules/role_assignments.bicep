targetScope = 'resourceGroup'

param openAiName string
param searchName string
param storageAccountName string
param keyVaultName string
param acrName string

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

resource developerOpenAiAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(developerPrincipalId)) {
  name: guid(openAi.id, developerPrincipalId, cognitiveServicesOpenAiUserRoleDefinitionId)
  scope: openAi
  properties: {
    principalId: developerPrincipalId
    principalType: developerPrincipalType
    roleDefinitionId: cognitiveServicesOpenAiUserRoleDefinitionId
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
