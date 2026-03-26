[CmdletBinding()]
param(
    [string]$SubscriptionId = $env:AZURE_SUBSCRIPTION_ID,
    [string]$ResourceGroup = $env:AZURE_RESOURCE_GROUP,
    [string]$StateFile = (Join-Path $PSScriptRoot ".." ".day0" "full.json"),
    [string]$ImageName = "aegisap-api",
    [string]$ImageTag = "",
    [string]$Dockerfile = (Join-Path $PSScriptRoot ".." "docker" "Dockerfile.api")
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

if ([string]::IsNullOrWhiteSpace($ImageTag)) {
    if (-not [string]::IsNullOrWhiteSpace($env:GITHUB_SHA)) {
        $ImageTag = $env:GITHUB_SHA
    }
    else {
        $ImageTag = (git -C (Join-Path $PSScriptRoot "..") rev-parse --short=12 HEAD).Trim()
    }
}

az account set --subscription $SubscriptionId | Out-Null
Write-Host "Building and pushing image ${ImageName}:${ImageTag} to ACR $acrName using $Dockerfile..." -ForegroundColor Cyan
az acr build `
  --registry $acrName `
  --file $Dockerfile `
  --image "${ImageName}:${ImageTag}" `
  (Join-Path $PSScriptRoot "..")
