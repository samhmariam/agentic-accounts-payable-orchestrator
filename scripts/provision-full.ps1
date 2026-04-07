[CmdletBinding()]
param(
    [string]$SubscriptionId = $env:AZURE_SUBSCRIPTION_ID,
    [string]$ResourceGroup = $env:AZURE_RESOURCE_GROUP,
    [string]$Location = $env:AZURE_LOCATION,
    [string]$TemplateFile = (Join-Path $PSScriptRoot ".." "infra" "full.bicep"),
    [string]$RoleAssignmentsTemplateFile = (Join-Path $PSScriptRoot ".." "infra" "modules" "role_assignments.bicep"),
    [string]$ParameterFile = (Join-Path $PSScriptRoot ".." "infra" "full.bicepparam"),
    [string]$OutputsFile = (Join-Path $PSScriptRoot ".." ".day0" "full.json"),
    [string]$SearchIndexScript = (Join-Path $PSScriptRoot "ensure_search_index.py"),
    [string]$Day3SearchIndexScript = (Join-Path $PSScriptRoot "ensure_day3_search_index.py"),
    [string]$Day3SearchIndexName = "day3-evidence",
    [string]$DeveloperPrincipalId,
    [string]$DeveloperPrincipalName,
    [ValidateSet("User", "ServicePrincipal", "Group", "Unknown")]
    [string]$DeveloperPrincipalType,
    [string]$PostgresEntraAdminObjectId,
    [string]$PostgresEntraAdminName,
    [ValidateSet("User", "ServicePrincipal", "Group", "Unknown")]
    [string]$PostgresEntraAdminType,
    [string]$WorkloadIdentityName = "id-aegisap-workload",
    [string]$JobsIdentityName = "id-aegisap-jobs",
    [string]$SearchAdminIdentityName = "id-aegisap-search-admin",
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
$RoleAssignmentsTemplateFile = Resolve-ExistingPath -PathValue $RoleAssignmentsTemplateFile -Name "RoleAssignmentsTemplateFile"
if (-not (Test-Path -LiteralPath $ParameterFile)) {
    throw "Parameter file not found: $ParameterFile. Copy infra/full.bicepparam.example to infra/full.bicepparam and fill in the placeholders."
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

if ([string]::IsNullOrWhiteSpace($PostgresEntraAdminObjectId)) {
    $PostgresEntraAdminObjectId = $DeveloperPrincipalId
}
if ([string]::IsNullOrWhiteSpace($PostgresEntraAdminName)) {
    $PostgresEntraAdminName = $DeveloperPrincipalName
}
if ([string]::IsNullOrWhiteSpace($PostgresEntraAdminType)) {
    $PostgresEntraAdminType = $DeveloperPrincipalType
}

Write-Host "Deploying full Day 0 platform resources..." -ForegroundColor Cyan
$deployment = Invoke-AzJson -Arguments @(
    "deployment", "group", "create",
    "--resource-group", $ResourceGroup,
    "--template-file", $TemplateFile,
    "--parameters", $ParameterFile,
    "--parameters", "location=$Location",
    "--parameters", "postgresEntraAdminObjectId=$PostgresEntraAdminObjectId",
    "--parameters", "postgresEntraAdminName=$PostgresEntraAdminName",
    "--parameters", "postgresEntraAdminType=$PostgresEntraAdminType",
    "--parameters", "workloadIdentityName=$WorkloadIdentityName",
    "--parameters", "jobsIdentityName=$JobsIdentityName",
    "--parameters", "searchAdminIdentityName=$SearchAdminIdentityName"
)

$outputs = $deployment.properties.outputs

if (-not $SkipRoleAssignments) {
    Write-Host "Applying full-track RBAC role assignments..." -ForegroundColor Cyan
    $openAiName = Get-OutputValue -Outputs $outputs -Name "openAiName"
    $searchName = Get-OutputValue -Outputs $outputs -Name "searchName"
    $storageAccountName = Get-OutputValue -Outputs $outputs -Name "storageAccountName"
    $keyVaultName = (Get-OutputValue -Outputs $outputs -Name "keyVaultUri").Split("//")[1].Split(".")[0]
    $acrName = Get-OutputValue -Outputs $outputs -Name "acrName"
    $workloadIdentityPrincipalId = Get-OutputValue -Outputs $outputs -Name "workloadIdentityPrincipalId"
    $jobsIdentityPrincipalId = Get-OutputValue -Outputs $outputs -Name "jobsIdentityPrincipalId"
    $searchAdminIdentityPrincipalId = Get-OutputValue -Outputs $outputs -Name "searchAdminIdentityPrincipalId"
    $cognitiveServicesOpenAiUserRoleDefinitionId = Get-RoleDefinitionId "Cognitive Services OpenAI User"
    $searchIndexDataReaderRoleDefinitionId = Get-RoleDefinitionId "Search Index Data Reader"
    $searchIndexDataContributorRoleDefinitionId = Get-RoleDefinitionId "Search Index Data Contributor"
    $searchServiceContributorRoleDefinitionId = Get-RoleDefinitionId "Search Service Contributor"
    $storageBlobDataReaderRoleDefinitionId = Get-RoleDefinitionId "Storage Blob Data Reader"
    $storageBlobDataContributorRoleDefinitionId = Get-RoleDefinitionId "Storage Blob Data Contributor"
    $keyVaultUserRoleId = Get-RoleDefinitionId "Key Vault Secrets User"
    $acrPullRoleDefinitionId = Get-RoleDefinitionId "AcrPull"

    Invoke-AzText -Arguments @(
        "deployment", "group", "create",
        "--resource-group", $ResourceGroup,
        "--template-file", $RoleAssignmentsTemplateFile,
        "--parameters", "openAiName=$openAiName",
        "--parameters", "searchName=$searchName",
        "--parameters", "storageAccountName=$storageAccountName",
        "--parameters", "keyVaultName=$keyVaultName",
        "--parameters", "acrName=$acrName",
        "--parameters", "developerPrincipalId=$DeveloperPrincipalId",
        "--parameters", "developerPrincipalType=$DeveloperPrincipalType",
        "--parameters", "pullIdentityPrincipalId=$workloadIdentityPrincipalId",
        "--parameters", "jobsIdentityPrincipalId=$jobsIdentityPrincipalId",
        "--parameters", "searchAdminIdentityPrincipalId=$searchAdminIdentityPrincipalId",
        "--parameters", "cognitiveServicesOpenAiUserRoleDefinitionId=$cognitiveServicesOpenAiUserRoleDefinitionId",
        "--parameters", "searchIndexDataReaderRoleDefinitionId=$searchIndexDataReaderRoleDefinitionId",
        "--parameters", "searchIndexDataContributorRoleDefinitionId=$searchIndexDataContributorRoleDefinitionId",
        "--parameters", "searchServiceContributorRoleDefinitionId=$searchServiceContributorRoleDefinitionId",
        "--parameters", "storageBlobDataReaderRoleDefinitionId=$storageBlobDataReaderRoleDefinitionId",
        "--parameters", "storageBlobDataContributorRoleDefinitionId=$storageBlobDataContributorRoleDefinitionId",
        "--parameters", "keyVaultUserRoleId=$keyVaultUserRoleId",
        "--parameters", "acrPullRoleDefinitionId=$acrPullRoleDefinitionId",
        "-o", "none"
    ) | Out-Null
}

Ensure-FoundryChatDeployment `
    -ResourceGroup $ResourceGroup `
    -FoundryName (Get-OutputValue -Outputs $outputs -Name "foundryName") `
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
    AZURE_FOUNDRY_ENDPOINT = Get-OutputValue -Outputs $outputs -Name "foundryEndpoint"
    AZURE_FOUNDRY_RESOURCE_NAME = Get-OutputValue -Outputs $outputs -Name "foundryName"
    AZURE_OPENAI_ENDPOINT = Get-OutputValue -Outputs $outputs -Name "openAiEndpoint"
    AZURE_OPENAI_API_VERSION = Get-OutputValue -Outputs $outputs -Name "openAiApiVersion"
    AZURE_OPENAI_CHAT_DEPLOYMENT = Get-OutputValue -Outputs $outputs -Name "openAiChatDeploymentName"
    AZURE_SEARCH_ENDPOINT = Get-OutputValue -Outputs $outputs -Name "searchEndpoint"
    AZURE_SEARCH_INDEX = Get-OutputValue -Outputs $outputs -Name "searchIndexName"
    AZURE_SEARCH_DAY3_INDEX = $Day3SearchIndexName
    AZURE_STORAGE_ACCOUNT_URL = Get-OutputValue -Outputs $outputs -Name "storageAccountUrl"
    AZURE_STORAGE_CONTAINER = Get-OutputValue -Outputs $outputs -Name "storageContainerName"
    AZURE_POSTGRES_HOST = Get-OutputValue -Outputs $outputs -Name "postgresHost"
    AZURE_POSTGRES_PORT = "5432"
    AZURE_POSTGRES_DB = Get-OutputValue -Outputs $outputs -Name "postgresDatabaseName"
    AZURE_POSTGRES_USER = Get-OutputValue -Outputs $outputs -Name "postgresUser"
    AZURE_KEY_VAULT_URI = Get-OutputValue -Outputs $outputs -Name "keyVaultUri"
    APPLICATIONINSIGHTS_CONNECTION_STRING = Get-OutputValue -Outputs $outputs -Name "appInsightsConnectionString"
}

$resources = [ordered]@{
    foundryName = Get-OutputValue -Outputs $outputs -Name "foundryName"
    acrName = Get-OutputValue -Outputs $outputs -Name "acrName"
    acrLoginServer = Get-OutputValue -Outputs $outputs -Name "acrLoginServer"
    openAiName = Get-OutputValue -Outputs $outputs -Name "openAiName"
    searchName = Get-OutputValue -Outputs $outputs -Name "searchName"
    searchDay3IndexName = $Day3SearchIndexName
    storageAccountName = Get-OutputValue -Outputs $outputs -Name "storageAccountName"
    containerAppsEnvironmentId = Get-OutputValue -Outputs $outputs -Name "containerAppsEnvironmentId"
    containerAppsEnvironmentName = Get-OutputValue -Outputs $outputs -Name "containerAppsEnvironmentName"
    postgresServerName = Get-OutputValue -Outputs $outputs -Name "postgresServerName"
    keyVaultUri = Get-OutputValue -Outputs $outputs -Name "keyVaultUri"
    workloadIdentityClientId = Get-OutputValue -Outputs $outputs -Name "workloadIdentityClientId"
    workloadIdentityResourceId = Get-OutputValue -Outputs $outputs -Name "workloadIdentityResourceId"
    jobsIdentityClientId = Get-OutputValue -Outputs $outputs -Name "jobsIdentityClientId"
    jobsIdentityResourceId = Get-OutputValue -Outputs $outputs -Name "jobsIdentityResourceId"
    searchAdminIdentityClientId = Get-OutputValue -Outputs $outputs -Name "searchAdminIdentityClientId"
    searchAdminIdentityResourceId = Get-OutputValue -Outputs $outputs -Name "searchAdminIdentityResourceId"
    developerPrincipalName = $DeveloperPrincipalName
    postgresEntraAdminName = $PostgresEntraAdminName
}

Write-Day0State `
    -OutputsFile $OutputsFile `
    -Track "full" `
    -SubscriptionId $SubscriptionId `
    -ResourceGroup $ResourceGroup `
    -Location $Location `
    -Environment $environment `
    -Resources $resources

Write-Host ""
Write-Host "Full Day 0 provisioning complete with a Foundry-first baseline." -ForegroundColor Green
Write-Host "State file: $OutputsFile"
Write-Host "Next: . ./scripts/setup-env.ps1 -Track full"
Write-Host "Then: python scripts/verify_env.py --track full"
Write-Host "Optional Day 3 live ingest: python scripts/ingest_day3_search_docs.py"
Write-Host "Optional Day 3 live verify: python scripts/verify_day3_live_retrieval.py"
