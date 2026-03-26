targetScope = 'resourceGroup'

@description('Azure location')
param location string = resourceGroup().location
param appName string = 'ca-aegisap-staging'
param containerAppsEnvironmentId string
param workloadIdentityResourceId string
param acrLoginServer string
param imageName string
param serviceName string = 'aegisap-api'
param gitSha string = 'dev'
param imageTag string = 'dev'
param deploymentRevision string = 'staging'
param applicationInsightsConnectionString string = ''
param traceSampleRatio string = '1.0'
param tracingEnabled string = 'true'
param langsmithTracing string = 'true'
param langsmithProject string = 'aegisap-staging'
param langsmithEndpoint string = ''
param langsmithApiKeySecretName string = 'aegisap-langsmith-api-key'
param resumeTokenSecretName string = 'aegisap-resume-token-secret'
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

module stagingApp '../modules/container_app.bicep' = {
  name: 'stagingApp'
  params: {
    location: location
    appName: appName
    containerAppsEnvironmentId: containerAppsEnvironmentId
    workloadIdentityResourceId: workloadIdentityResourceId
    acrLoginServer: acrLoginServer
    imageName: imageName
    serviceName: serviceName
    gitSha: gitSha
    imageTag: imageTag
    resumeTokenSecretName: resumeTokenSecretName
    runtimeEnvironment: 'staging'
    revisionSuffix: gitSha
    applicationInsightsConnectionString: applicationInsightsConnectionString
    deploymentRevision: deploymentRevision
    traceSampleRatio: traceSampleRatio
    tracingEnabled: tracingEnabled
    langsmithTracing: langsmithTracing
    langsmithProject: langsmithProject
    langsmithEndpoint: langsmithEndpoint
    langsmithApiKeySecretName: langsmithApiKeySecretName
    azureOpenAiEndpoint: azureOpenAiEndpoint
    azureOpenAiApiVersion: azureOpenAiApiVersion
    azureOpenAiChatDeployment: azureOpenAiChatDeployment
    azureSearchEndpoint: azureSearchEndpoint
    azureSearchDay3Index: azureSearchDay3Index
    azureStorageAccountUrl: azureStorageAccountUrl
    azureStorageContainer: azureStorageContainer
    azurePostgresHost: azurePostgresHost
    azurePostgresPort: azurePostgresPort
    azurePostgresDb: azurePostgresDb
    azurePostgresUser: azurePostgresUser
    azureKeyVaultUri: azureKeyVaultUri
    targetPort: targetPort
  }
}

output appUrl string = stagingApp.outputs.appUrl
output runtimePrincipalId string = stagingApp.outputs.runtimePrincipalId
output latestRevisionName string = stagingApp.outputs.latestRevisionName
