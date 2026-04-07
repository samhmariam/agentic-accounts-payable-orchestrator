targetScope = 'resourceGroup'

@description('Primary region')
param location string = resourceGroup().location

@description('Storage account name')
param storageAccountName string

@description('Blob container name for source documents')
param storageContainerName string = 'documents'

resource st 'Microsoft.Storage/storageAccounts@2025-06-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    allowBlobPublicAccess: false
    allowSharedKeyAccess: false
    defaultToOAuthAuthentication: true
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
  }
}

resource stBlob 'Microsoft.Storage/storageAccounts/blobServices@2025-06-01' = {
  parent: st
  name: 'default'
}

resource stContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2025-06-01' = {
  parent: stBlob
  name: storageContainerName
  properties: {
    publicAccess: 'None'
  }
}

output storageAccountId string = st.id
output storageAccountName string = st.name
output storageAccountUrl string = st.properties.primaryEndpoints.blob
output storageContainerName string = stContainer.name
