[CmdletBinding()]
param(
    [ValidateSet("core", "full")]
    [string]$Track = "core",
    [string]$OutputsFile
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-RequiredValue {
    param(
        [AllowEmptyString()]
        [string]$Value,
        [string]$Name
    )

    if ([string]::IsNullOrWhiteSpace($Value)) {
        throw "Missing required value for $Name in the Day 0 state file."
    }

    return $Value
}

if ([string]::IsNullOrWhiteSpace($OutputsFile)) {
    $OutputsFile = Join-Path $PSScriptRoot ".." ".day0" "$Track.json"
}

if (-not (Test-Path -LiteralPath $OutputsFile)) {
    throw "Day 0 state file not found: $OutputsFile. Run scripts/provision-$Track.ps1 first."
}

$OutputsFile = (Resolve-Path -LiteralPath $OutputsFile).Path
$state = Get-Content -LiteralPath $OutputsFile -Raw | ConvertFrom-Json

if (-not $state.environment) {
    throw "Day 0 state file is missing the 'environment' object: $OutputsFile"
}

if ($state.track -and $state.track -ne $Track) {
    Write-Warning "State file track '$($state.track)' does not match requested track '$Track'. Loading the file anyway."
}

$requiredVars = @(
    "AZURE_SUBSCRIPTION_ID",
    "AZURE_RESOURCE_GROUP",
    "AZURE_LOCATION",
    "AZURE_OPENAI_ENDPOINT",
    "AZURE_OPENAI_API_VERSION",
    "AZURE_OPENAI_CHAT_DEPLOYMENT",
    "AZURE_SEARCH_ENDPOINT",
    "AZURE_SEARCH_INDEX",
    "AZURE_STORAGE_ACCOUNT_URL",
    "AZURE_STORAGE_CONTAINER"
)

if ($Track -eq "full") {
    $requiredVars += @(
        "AZURE_POSTGRES_HOST",
        "AZURE_POSTGRES_PORT",
        "AZURE_POSTGRES_DB",
        "AZURE_POSTGRES_USER",
        "AZURE_KEY_VAULT_URI",
        "APPLICATIONINSIGHTS_CONNECTION_STRING"
    )
}

Write-Host "Loading Day 0 environment for track '$Track' from $OutputsFile" -ForegroundColor Cyan

foreach ($property in $state.environment.PSObject.Properties) {
    if ($null -ne $property.Value -and -not [string]::IsNullOrWhiteSpace([string]$property.Value)) {
        [Environment]::SetEnvironmentVariable($property.Name, [string]$property.Value, "Process")
    }
}

if ([string]::IsNullOrWhiteSpace([Environment]::GetEnvironmentVariable("AEGISAP_ENVIRONMENT", "Process"))) {
    [Environment]::SetEnvironmentVariable("AEGISAP_ENVIRONMENT", "local", "Process")
}

if ([string]::IsNullOrWhiteSpace([Environment]::GetEnvironmentVariable("AEGISAP_RESUME_TOKEN_SECRET_NAME", "Process"))) {
    [Environment]::SetEnvironmentVariable("AEGISAP_RESUME_TOKEN_SECRET_NAME", "aegisap-resume-token-secret", "Process")
}

foreach ($key in $requiredVars) {
    $property = $state.environment.PSObject.Properties[$key]
    $value = if ($property) { [string]$property.Value } else { "" }
    Get-RequiredValue -Value ([string]$value) -Name $key | Out-Null
}

Write-Host "Done. Azure auth still comes from az login or DefaultAzureCredential environment variables." -ForegroundColor Green
