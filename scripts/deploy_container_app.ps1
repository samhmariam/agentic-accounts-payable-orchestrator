[CmdletBinding()]
param(
    [string]$SubscriptionId = $env:AZURE_SUBSCRIPTION_ID,
    [string]$ResourceGroup = $env:AZURE_RESOURCE_GROUP,
    [string]$Location = $env:AZURE_LOCATION,
    [string]$StateFile = (Join-Path $PSScriptRoot ".." ".day0" "full.json"),
    [ValidateSet("staging", "production")]
    [string]$EnvironmentName = "staging",
    [string]$TemplateFile = "",
    [string]$RoleAssignmentsTemplateFile = (Join-Path $PSScriptRoot ".." "infra" "modules" "role_assignments.bicep"),
    [string]$AppName = "",
    [string]$ImageName = "aegisap-api",
    [string]$ImageTag = "",
    [string]$DeploymentRevision = "",
    [string]$ResumeTokenSecretName = "aegisap-resume-token-secret",
    [string]$ResumeTokenSecretValue = $env:AEGISAP_RESUME_TOKEN_SECRET,
    [string]$LangSmithProject = $env:LANGSMITH_PROJECT,
    [string]$LangSmithEndpoint = $env:LANGSMITH_ENDPOINT,
    [string]$LangSmithApiKeySecretName = "aegisap-langsmith-api-key",
    [string]$ServiceName = "aegisap-api",
    [string]$GitSha = "",
    [string]$TraceSampleRatio = "",
    [string]$TracingEnabled = "true",
    [string]$LangSmithTracing = "true"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "day0-common.ps1")

if (-not (Test-Path -LiteralPath $StateFile)) {
    throw "State file not found: $StateFile"
}

$state = Get-Content -LiteralPath $StateFile -Raw | ConvertFrom-Json
$envVars = $state.environment
$resources = $state.resources

if ([string]::IsNullOrWhiteSpace($TemplateFile)) {
    $templateName = if ($EnvironmentName -eq "production") { "prod.bicep" } else { "staging.bicep" }
    $TemplateFile = (Join-Path $PSScriptRoot ".." "infra" "aca" $templateName)
}

if ([string]::IsNullOrWhiteSpace($AppName)) {
    $AppName = if ($EnvironmentName -eq "production") { "ca-aegisap-prod" } else { "ca-aegisap-staging" }
}

if ([string]::IsNullOrWhiteSpace($GitSha)) {
    if (-not [string]::IsNullOrWhiteSpace($env:GITHUB_SHA)) {
        $GitSha = $env:GITHUB_SHA
    }
    else {
        $GitSha = (git -C (Join-Path $PSScriptRoot "..") rev-parse --short=12 HEAD).Trim()
    }
}

if ([string]::IsNullOrWhiteSpace($ImageTag)) {
    $ImageTag = $GitSha
}

if ([string]::IsNullOrWhiteSpace($DeploymentRevision)) {
    $DeploymentRevision = "${EnvironmentName}-${GitSha}"
}

if ([string]::IsNullOrWhiteSpace($TraceSampleRatio)) {
    $TraceSampleRatio = if ($EnvironmentName -eq "production") { "0.25" } else { "1.0" }
}

if ([string]::IsNullOrWhiteSpace($resources.acrName) -or [string]::IsNullOrWhiteSpace($resources.containerAppsEnvironmentId)) {
    throw "Missing full-track deployment metadata in $StateFile."
}

$acrLoginServer = az acr show --name $resources.acrName --query loginServer -o tsv
$imageRef = "${acrLoginServer}/${ImageName}:${ImageTag}"
$keyVaultName = $resources.keyVaultUri.Replace("https://", "").Split(".")[0]

if ([string]::IsNullOrWhiteSpace($ResumeTokenSecretValue)) {
    $ResumeTokenSecretValue = "dev-only-resume-secret"
}

az account set --subscription $SubscriptionId | Out-Null

Write-Host "Writing runtime resume token secret into Key Vault..." -ForegroundColor Cyan
az keyvault secret set `
  --vault-name $keyVaultName `
  --name $ResumeTokenSecretName `
  --value $ResumeTokenSecretValue `
  --only-show-errors `
  -o none

Write-Host "Deploying container app $AppName..." -ForegroundColor Cyan
$deployment = az deployment group create `
  --resource-group $ResourceGroup `
  --template-file $TemplateFile `
  --parameters location=$Location `
  --parameters appName=$AppName `
  --parameters containerAppsEnvironmentId=$resources.containerAppsEnvironmentId `
  --parameters workloadIdentityResourceId=$resources.workloadIdentityResourceId `
  --parameters acrLoginServer=$acrLoginServer `
  --parameters imageName=$imageRef `
  --parameters serviceName=$ServiceName `
  --parameters gitSha=$GitSha `
  --parameters imageTag=$ImageTag `
  --parameters resumeTokenSecretName=$ResumeTokenSecretName `
  --parameters deploymentRevision=$DeploymentRevision `
  --parameters traceSampleRatio=$TraceSampleRatio `
  --parameters tracingEnabled=$TracingEnabled `
  --parameters langsmithTracing=$LangSmithTracing `
  --parameters langsmithProject=$LangSmithProject `
  --parameters langsmithEndpoint=$LangSmithEndpoint `
  --parameters langsmithApiKeySecretName=$LangSmithApiKeySecretName `
  --parameters applicationInsightsConnectionString=$envVars.APPLICATIONINSIGHTS_CONNECTION_STRING `
  --parameters azureOpenAiEndpoint=$envVars.AZURE_OPENAI_ENDPOINT `
  --parameters azureOpenAiApiVersion=$envVars.AZURE_OPENAI_API_VERSION `
  --parameters azureOpenAiChatDeployment=$envVars.AZURE_OPENAI_CHAT_DEPLOYMENT `
  --parameters azureSearchEndpoint=$envVars.AZURE_SEARCH_ENDPOINT `
  --parameters azureSearchDay3Index=$envVars.AZURE_SEARCH_DAY3_INDEX `
  --parameters azureStorageAccountUrl=$envVars.AZURE_STORAGE_ACCOUNT_URL `
  --parameters azureStorageContainer=$envVars.AZURE_STORAGE_CONTAINER `
  --parameters azurePostgresHost=$envVars.AZURE_POSTGRES_HOST `
  --parameters azurePostgresPort=$envVars.AZURE_POSTGRES_PORT `
  --parameters azurePostgresDb=$envVars.AZURE_POSTGRES_DB `
  --parameters azurePostgresUser=$envVars.AZURE_POSTGRES_USER `
  --parameters azureKeyVaultUri=$envVars.AZURE_KEY_VAULT_URI `
  --only-show-errors `
  -o json | ConvertFrom-Json

$runtimePrincipalId = $deployment.properties.outputs.runtimePrincipalId.value

Write-Host "Applying runtime RBAC role assignments..." -ForegroundColor Cyan
az deployment group create `
  --resource-group $ResourceGroup `
  --template-file $RoleAssignmentsTemplateFile `
  --parameters openAiName=$resources.openAiName `
  --parameters searchName=$resources.searchName `
  --parameters storageAccountName=$resources.storageAccountName `
  --parameters keyVaultName=$keyVaultName `
  --parameters acrName=$resources.acrName `
  --parameters runtimeApiPrincipalId=$runtimePrincipalId `
  --parameters cognitiveServicesOpenAiUserRoleDefinitionId=$(Get-RoleDefinitionId "Cognitive Services OpenAI User") `
  --parameters searchIndexDataReaderRoleDefinitionId=$(Get-RoleDefinitionId "Search Index Data Reader") `
  --parameters searchIndexDataContributorRoleDefinitionId=$(Get-RoleDefinitionId "Search Index Data Contributor") `
  --parameters searchServiceContributorRoleDefinitionId=$(Get-RoleDefinitionId "Search Service Contributor") `
  --parameters storageBlobDataReaderRoleDefinitionId=$(Get-RoleDefinitionId "Storage Blob Data Reader") `
  --parameters storageBlobDataContributorRoleDefinitionId=$(Get-RoleDefinitionId "Storage Blob Data Contributor") `
  --parameters keyVaultUserRoleId=$(Get-RoleDefinitionId "Key Vault Secrets User") `
  --parameters acrPullRoleDefinitionId=$(Get-RoleDefinitionId "AcrPull") `
  --only-show-errors `
  -o none

$appUrl = $deployment.properties.outputs.appUrl.value
$latestRevisionName = $deployment.properties.outputs.latestRevisionName.value
Write-Host "Deployment complete." -ForegroundColor Green
Write-Host "App URL: $appUrl"
Write-Host "Latest revision: $latestRevisionName"
