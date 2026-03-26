targetScope = 'resourceGroup'

param location string = resourceGroup().location
param appName string
param containerAppsEnvironmentId string
param workloadIdentityResourceId string
param acrLoginServer string
param imageName string
param resumeTokenSecretName string = 'aegisap-resume-token-secret'
param runtimeEnvironment string = 'cloud'

param applicationInsightsConnectionString string = ''
param azureOpenAiEndpoint string
param azureOpenAiApiVersion string
param azureOpenAiChatDeployment string
param azureSearchEndpoint string
param azureSearchDay3Index string
param azureStorageAccountUrl string
param azureStorageContainer string
param azurePostgresHost string
param azurePostgresPort string = '5432'
param azurePostgresDb string
param azurePostgresUser string
param azureKeyVaultUri string = ''
param targetPort int = 8000

resource app 'Microsoft.App/containerApps@2024-03-01' = {
  name: appName
  location: location
  identity: {
    type: 'SystemAssigned,UserAssigned'
    userAssignedIdentities: {
      '${workloadIdentityResourceId}': {}
    }
  }
  properties: {
    managedEnvironmentId: containerAppsEnvironmentId
    configuration: {
      ingress: {
        external: true
        targetPort: targetPort
        transport: 'auto'
      }
      registries: [
        {
          server: acrLoginServer
          identity: workloadIdentityResourceId
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'api'
          image: imageName
          resources: {
            cpu: json('0.5')
            memory: '1.0Gi'
          }
          env: [
            {
              name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
              value: applicationInsightsConnectionString
            }
            {
              name: 'AEGISAP_ENVIRONMENT'
              value: runtimeEnvironment
            }
            {
              name: 'AZURE_OPENAI_ENDPOINT'
              value: azureOpenAiEndpoint
            }
            {
              name: 'AZURE_OPENAI_API_VERSION'
              value: azureOpenAiApiVersion
            }
            {
              name: 'AZURE_OPENAI_CHAT_DEPLOYMENT'
              value: azureOpenAiChatDeployment
            }
            {
              name: 'AZURE_SEARCH_ENDPOINT'
              value: azureSearchEndpoint
            }
            {
              name: 'AZURE_SEARCH_DAY3_INDEX'
              value: azureSearchDay3Index
            }
            {
              name: 'AZURE_STORAGE_ACCOUNT_URL'
              value: azureStorageAccountUrl
            }
            {
              name: 'AZURE_STORAGE_CONTAINER'
              value: azureStorageContainer
            }
            {
              name: 'AZURE_POSTGRES_HOST'
              value: azurePostgresHost
            }
            {
              name: 'AZURE_POSTGRES_PORT'
              value: azurePostgresPort
            }
            {
              name: 'AZURE_POSTGRES_DB'
              value: azurePostgresDb
            }
            {
              name: 'AZURE_POSTGRES_USER'
              value: azurePostgresUser
            }
            {
              name: 'AZURE_KEY_VAULT_URI'
              value: azureKeyVaultUri
            }
            {
              name: 'AEGISAP_RESUME_TOKEN_SECRET_NAME'
              value: resumeTokenSecretName
            }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 1
      }
    }
  }
}

output appUrl string = app.properties.configuration.ingress.fqdn == '' ? '' : 'https://${app.properties.configuration.ingress.fqdn}'
output runtimePrincipalId string = app.identity.principalId
