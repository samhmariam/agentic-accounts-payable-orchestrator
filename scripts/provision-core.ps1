[CmdletBinding()]
param(
    [string]$SubscriptionId = $env:AZURE_SUBSCRIPTION_ID,
    [string]$ResourceGroup = $env:AZURE_RESOURCE_GROUP,
    [string]$Location = $env:AZURE_LOCATION,
    [string]$TemplateFile = (Join-Path $PSScriptRoot ".." "infra" "core.bicep"),
    [string]$ParameterFile = (Join-Path $PSScriptRoot ".." "infra" "core.bicepparam"),
    [string]$OutputsFile = (Join-Path $PSScriptRoot ".." ".day0" "core.json"),
    [string]$SearchIndexScript = (Join-Path $PSScriptRoot "ensure_search_index.py"),
    [string]$Day3SearchIndexScript = (Join-Path $PSScriptRoot "ensure_day3_search_index.py"),
    [string]$Day3SearchIndexName = "day3-evidence",
    [string]$DeveloperPrincipalId,
    [string]$DeveloperPrincipalName,
    [ValidateSet("User", "ServicePrincipal", "Group", "Unknown")]
    [string]$DeveloperPrincipalType,
    [switch]$SkipRoleAssignments
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "day0-common.ps1")

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$SubscriptionId = Get-RequiredValue -Value $SubscriptionId -Name "SubscriptionId / AZURE_SUBSCRIPTION_ID"
$ResourceGroup = Get-RequiredValue -Value $ResourceGroup -Name "ResourceGroup / AZURE_RESOURCE_GROUP"
$Location = Get-RequiredValue -Value $Location -Name "Location / AZURE_LOCATION"
$TemplateFile = Resolve-ExistingPath -PathValue $TemplateFile -Name "TemplateFile"
if (-not (Test-Path -LiteralPath $ParameterFile)) {
    throw "Parameter file not found: $ParameterFile. Copy infra/core.bicepparam.example to infra/core.bicepparam and fill in the placeholders."
}
$ParameterFile = Resolve-ExistingPath -PathValue $ParameterFile -Name "ParameterFile"
Assert-NoPlaceholderParameters -ParameterFile $ParameterFile
$SearchIndexScript = Resolve-ExistingPath -PathValue $SearchIndexScript -Name "SearchIndexScript"
$Day3SearchIndexScript = Resolve-ExistingPath -PathValue $Day3SearchIndexScript -Name "Day3SearchIndexScript"
$OutputsFile = [IO.Path]::GetFullPath($OutputsFile)

Invoke-AzText -Arguments @("account", "show", "-o", "none") | Out-Null
Invoke-AzText -Arguments @("account", "set", "--subscription", $SubscriptionId, "-o", "none") | Out-Null
Invoke-AzText -Arguments @("group", "create", "--name", $ResourceGroup, "--location", $Location, "-o", "none") | Out-Null

if ([string]::IsNullOrWhiteSpace($DeveloperPrincipalId) -or
    [string]::IsNullOrWhiteSpace($DeveloperPrincipalName) -or
    [string]::IsNullOrWhiteSpace($DeveloperPrincipalType)) {
    $account = Invoke-AzJson -Arguments @("account", "show")
    if ($account.user.type -ne "user") {
        throw "DeveloperPrincipalId, DeveloperPrincipalName, and DeveloperPrincipalType are required when Azure CLI is authenticated as '$($account.user.type)'."
    }

    $signedInUser = Invoke-AzJson -Arguments @("ad", "signed-in-user", "show")
    $DeveloperPrincipalId = $signedInUser.id
    $DeveloperPrincipalName = $signedInUser.userPrincipalName
    $DeveloperPrincipalType = "User"
}

Write-Host "Deploying core Day 0 resources..." -ForegroundColor Cyan
$deployment = Invoke-AzJson -Arguments @(
    "deployment", "group", "create",
    "--resource-group", $ResourceGroup,
    "--template-file", $TemplateFile,
    "--parameters", $ParameterFile,
    "--parameters", "location=$Location"
)

$outputs = $deployment.properties.outputs

if (-not $SkipRoleAssignments) {
    Write-Host "Applying core RBAC role assignments..." -ForegroundColor Cyan
    Ensure-RoleAssignment -PrincipalId $DeveloperPrincipalId -PrincipalType $DeveloperPrincipalType -RoleName "Cognitive Services OpenAI User" -Scope (Get-OutputValue -Outputs $outputs -Name "openAiId")
    Ensure-RoleAssignment -PrincipalId $DeveloperPrincipalId -PrincipalType $DeveloperPrincipalType -RoleName "Search Service Contributor" -Scope (Get-OutputValue -Outputs $outputs -Name "searchServiceId")
    Ensure-RoleAssignment -PrincipalId $DeveloperPrincipalId -PrincipalType $DeveloperPrincipalType -RoleName "Search Index Data Contributor" -Scope (Get-OutputValue -Outputs $outputs -Name "searchServiceId")
    Ensure-RoleAssignment -PrincipalId $DeveloperPrincipalId -PrincipalType $DeveloperPrincipalType -RoleName "Storage Blob Data Contributor" -Scope (Get-OutputValue -Outputs $outputs -Name "storageAccountId")
}

Ensure-OpenAiDeployment `
    -ResourceGroup $ResourceGroup `
    -OpenAiName (Get-OutputValue -Outputs $outputs -Name "openAiName") `
    -DeploymentName (Get-OutputValue -Outputs $outputs -Name "openAiChatDeploymentName") `
    -ModelName (Get-OutputValue -Outputs $outputs -Name "openAiChatModelName") `
    -ModelVersion (Get-OutputValue -Outputs $outputs -Name "openAiChatModelVersion") `
    -SkuName (Get-OutputValue -Outputs $outputs -Name "openAiChatSkuName") `
    -Capacity (Get-OutputValue -Outputs $outputs -Name "openAiChatCapacity")

Ensure-SearchIndex `
    -RepoRoot $repoRoot `
    -SearchEndpoint (Get-OutputValue -Outputs $outputs -Name "searchEndpoint") `
    -IndexName (Get-OutputValue -Outputs $outputs -Name "searchIndexName") `
    -SearchIndexScript $SearchIndexScript

Ensure-SearchIndex `
    -RepoRoot $repoRoot `
    -SearchEndpoint (Get-OutputValue -Outputs $outputs -Name "searchEndpoint") `
    -IndexName $Day3SearchIndexName `
    -SearchIndexScript $Day3SearchIndexScript

$environment = [ordered]@{
    AZURE_SUBSCRIPTION_ID = $SubscriptionId
    AZURE_RESOURCE_GROUP = $ResourceGroup
    AZURE_LOCATION = $Location
    AZURE_OPENAI_ENDPOINT = Get-OutputValue -Outputs $outputs -Name "openAiEndpoint"
    AZURE_OPENAI_API_VERSION = Get-OutputValue -Outputs $outputs -Name "openAiApiVersion"
    AZURE_OPENAI_CHAT_DEPLOYMENT = Get-OutputValue -Outputs $outputs -Name "openAiChatDeploymentName"
    AZURE_SEARCH_ENDPOINT = Get-OutputValue -Outputs $outputs -Name "searchEndpoint"
    AZURE_SEARCH_INDEX = Get-OutputValue -Outputs $outputs -Name "searchIndexName"
    AZURE_SEARCH_DAY3_INDEX = $Day3SearchIndexName
    AZURE_STORAGE_ACCOUNT_URL = Get-OutputValue -Outputs $outputs -Name "storageAccountUrl"
    AZURE_STORAGE_CONTAINER = Get-OutputValue -Outputs $outputs -Name "storageContainerName"
}

$resources = [ordered]@{
    openAiName = Get-OutputValue -Outputs $outputs -Name "openAiName"
    searchName = Get-OutputValue -Outputs $outputs -Name "searchName"
    searchDay3IndexName = $Day3SearchIndexName
    storageAccountName = Get-OutputValue -Outputs $outputs -Name "storageAccountName"
    developerPrincipalName = $DeveloperPrincipalName
}

Write-Day0State `
    -OutputsFile $OutputsFile `
    -Track "core" `
    -SubscriptionId $SubscriptionId `
    -ResourceGroup $ResourceGroup `
    -Location $Location `
    -Environment $environment `
    -Resources $resources

Write-Host ""
Write-Host "Core Day 0 provisioning complete." -ForegroundColor Green
Write-Host "State file: $OutputsFile"
Write-Host "Next: . ./scripts/setup-env.ps1 -Track core"
Write-Host "Then: python scripts/verify_env.py --track core"
Write-Host "Optional Day 3 live ingest: python scripts/ingest_day3_search_docs.py"
Write-Host "Optional Day 3 live verify: python scripts/verify_day3_live_retrieval.py"
