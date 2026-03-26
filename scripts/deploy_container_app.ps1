[CmdletBinding()]
param(
    [string]$SubscriptionId = $env:AZURE_SUBSCRIPTION_ID,
    [string]$ResourceGroup = $env:AZURE_RESOURCE_GROUP,
    [string]$Location = $env:AZURE_LOCATION,
    [string]$StateFile = (Join-Path $PSScriptRoot ".." ".day0" "full.json"),
    [string]$TemplateFile = (Join-Path $PSScriptRoot ".." "infra" "modules" "container_app.bicep"),
    [string]$AppName = "ca-aegisap-training",
    [string]$ImageName = "aegisap-training",
    [string]$ImageTag = "latest",
    [string]$ResumeTokenSecret = "dev-only-resume-secret"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $StateFile)) {
    throw "State file not found: $StateFile"
}

$state = Get-Content -LiteralPath $StateFile -Raw | ConvertFrom-Json
$envVars = $state.environment
$resources = $state.resources

if ([string]::IsNullOrWhiteSpace($resources.acrName) -or [string]::IsNullOrWhiteSpace($resources.containerAppsEnvironmentId)) {
    throw "Missing full-track deployment metadata in $StateFile."
}

$acrLoginServer = az acr show --name $resources.acrName --query loginServer -o tsv
$imageRef = "${acrLoginServer}/${ImageName}:${ImageTag}"

az account set --subscription $SubscriptionId | Out-Null

Write-Host "Deploying container app $AppName..." -ForegroundColor Cyan
az deployment group create `
  --resource-group $ResourceGroup `
  --template-file $TemplateFile `
  --parameters location=$Location `
  --parameters appName=$AppName `
  --parameters containerAppsEnvironmentId=$resources.containerAppsEnvironmentId `
  --parameters workloadIdentityResourceId=$resources.workloadIdentityResourceId `
  --parameters workloadIdentityClientId=$resources.workloadIdentityClientId `
  --parameters acrLoginServer=$acrLoginServer `
  --parameters imageName=$imageRef `
  --parameters resumeTokenSecret=$ResumeTokenSecret `
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
  --parameters azureKeyVaultUri=$envVars.AZURE_KEY_VAULT_URI
