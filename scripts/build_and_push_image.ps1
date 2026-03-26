[CmdletBinding()]
param(
    [string]$SubscriptionId = $env:AZURE_SUBSCRIPTION_ID,
    [string]$ResourceGroup = $env:AZURE_RESOURCE_GROUP,
    [string]$StateFile = (Join-Path $PSScriptRoot ".." ".day0" "full.json"),
    [string]$ImageName = "aegisap-training",
    [string]$ImageTag = "latest"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $StateFile)) {
    throw "State file not found: $StateFile"
}

$state = Get-Content -LiteralPath $StateFile -Raw | ConvertFrom-Json
$acrName = $state.resources.acrName
if ([string]::IsNullOrWhiteSpace($acrName)) {
    throw "acrName missing from $StateFile. Re-run full provisioning after updating the outputs."
}

az account set --subscription $SubscriptionId | Out-Null
Write-Host "Building and pushing image ${ImageName}:${ImageTag} to ACR $acrName..." -ForegroundColor Cyan
az acr build `
  --registry $acrName `
  --image "${ImageName}:${ImageTag}" `
  (Join-Path $PSScriptRoot "..")
