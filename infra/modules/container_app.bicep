targetScope = 'resourceGroup'

param location string = resourceGroup().location
param appName string
param containerAppsEnvironmentId string
param workloadIdentityResourceId string
param acrLoginServer string
param imageName string
param serviceName string = 'aegisap-api'
param gitSha string = 'dev'
param imageTag string = 'dev'
param resumeTokenSecretName string = 'aegisap-resume-token-secret'
param runtimeEnvironment string = 'cloud'
param revisionSuffix string = 'dev'

param applicationInsightsConnectionString string = ''
param deploymentRevision string = 'dev'
param traceSampleRatio string = '1.0'
param tracingEnabled string = 'true'
param langsmithTracing string = 'true'
param langsmithProject string = ''
param langsmithEndpoint string = ''
param langsmithApiKeySecretName string = 'aegisap-langsmith-api-key'
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
      activeRevisionsMode: 'multiple'
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
      revisionSuffix: revisionSuffix
      containers: [
        {
          name: 'api'
          image: imageName
          resources: {
            cpu: json('0.5')
            memory: '1.0Gi'
          }
          probes: [
            {
              type: 'Startup'
              httpGet: {
                path: '/health/live'
                port: targetPort
              }
              initialDelaySeconds: 10
              periodSeconds: 10
              timeoutSeconds: 5
              failureThreshold: 12
            }
            {
              type: 'Readiness'
              httpGet: {
                path: '/health/ready'
                port: targetPort
              }
              initialDelaySeconds: 10
              periodSeconds: 10
              timeoutSeconds: 5
              failureThreshold: 6
            }
            {
              type: 'Liveness'
              httpGet: {
                path: '/health/live'
                port: targetPort
              }
              initialDelaySeconds: 30
              periodSeconds: 15
              timeoutSeconds: 5
              failureThreshold: 4
            }
          ]
          env: [
            {
              name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
              value: applicationInsightsConnectionString
            }
            {
              name: 'AEGISAP_SERVICE_NAME'
              value: serviceName
            }
            {
              name: 'AEGISAP_ENVIRONMENT'
              value: runtimeEnvironment
            }
            {
              name: 'AEGISAP_DEPLOYMENT_REVISION'
              value: deploymentRevision
            }
            {
              name: 'AEGISAP_GIT_SHA'
              value: gitSha
            }
            {
              name: 'AEGISAP_IMAGE_TAG'
              value: imageTag
            }
            {
              name: 'AEGISAP_TRACE_SAMPLE_RATIO'
              value: traceSampleRatio
            }
            {
              name: 'AEGISAP_TRACING_ENABLED'
              value: tracingEnabled
            }
            {
              name: 'LANGSMITH_TRACING'
              value: langsmithTracing
            }
            {
              name: 'LANGSMITH_PROJECT'
              value: langsmithProject
            }
            {
              name: 'LANGSMITH_ENDPOINT'
              value: langsmithEndpoint
            }
            {
              name: 'AEGISAP_LANGSMITH_API_KEY_SECRET_NAME'
              value: langsmithApiKeySecretName
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
output latestRevisionName string = app.properties.latestRevisionName
