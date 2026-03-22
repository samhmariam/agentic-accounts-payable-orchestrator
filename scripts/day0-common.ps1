function Get-RequiredValue {
    param(
        [AllowEmptyString()]
        [string]$Value,
        [string]$Name
    )

    if ([string]::IsNullOrWhiteSpace($Value)) {
        throw "Missing required value for $Name."
    }

    return $Value
}

function Resolve-ExistingPath {
    param(
        [string]$PathValue,
        [string]$Name
    )

    if (-not (Test-Path -LiteralPath $PathValue)) {
        throw "$Name does not exist: $PathValue"
    }

    return (Resolve-Path -LiteralPath $PathValue).Path
}

function Convert-AzOutputToText {
    param(
        [AllowNull()]
        [object[]]$Output
    )

    if ($null -eq $Output) {
        return ""
    }

    $lines = foreach ($item in $Output) {
        if ($null -eq $item) {
            continue
        }

        if ($item -is [System.Management.Automation.ErrorRecord]) {
            if (-not [string]::IsNullOrWhiteSpace($item.Exception.Message)) {
                $item.Exception.Message
                continue
            }

            $item.ToString()
            continue
        }

        if ($item -is [string]) {
            $item
            continue
        }

        try {
            ($item | Out-String).TrimEnd()
        }
        catch {
            $item.ToString()
        }
    }

    return (($lines | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }) -join [Environment]::NewLine).Trim()
}

function Invoke-AzText {
    param(
        [string[]]$Arguments
    )

    $output = & az @Arguments --only-show-errors 2>&1
    $text = Convert-AzOutputToText -Output $output
    if ($LASTEXITCODE -ne 0) {
        throw $text
    }

    return $text
}

function Invoke-AzJson {
    param(
        [string[]]$Arguments
    )

    $raw = Invoke-AzText -Arguments (@($Arguments) + @("-o", "json"))
    if ([string]::IsNullOrWhiteSpace($raw)) {
        return $null
    }

    return $raw | ConvertFrom-Json
}

function Assert-NoPlaceholderParameters {
    param(
        [string]$ParameterFile
    )

    $content = Get-Content -LiteralPath $ParameterFile
    $matches = foreach ($line in $content) {
        if ($line -match "^\s*param\s+([A-Za-z0-9_]+)\s*=\s*'(<[^>]+>)'\s*$") {
            [PSCustomObject]@{
                Name = $matches[1]
                Placeholder = $matches[2]
            }
        }
    }

    if ($matches) {
        $details = ($matches | ForEach-Object { "$($_.Name)=$($_.Placeholder)" }) -join ", "
        throw "Parameter file contains placeholder values: $details. Update $ParameterFile before provisioning."
    }
}

function Ensure-RoleAssignment {
    param(
        [string]$PrincipalId,
        [string]$PrincipalType,
        [string]$RoleName,
        [string]$Scope
    )

    $count = Invoke-AzText -Arguments @(
        "role", "assignment", "list",
        "--assignee-object-id", $PrincipalId,
        "--scope", $Scope,
        "--query", "[?roleDefinitionName=='$RoleName'] | length(@)",
        "-o", "tsv"
    )

    if ($count -and [int]$count -gt 0) {
        Write-Host "Role assignment already present: $RoleName on $Scope" -ForegroundColor DarkGray
        return
    }

    Write-Host "Creating role assignment: $RoleName on $Scope" -ForegroundColor Cyan
    Invoke-AzText -Arguments @(
        "role", "assignment", "create",
        "--assignee-object-id", $PrincipalId,
        "--assignee-principal-type", $PrincipalType,
        "--role", $RoleName,
        "--scope", $Scope
    ) | Out-Null
}

function Get-OutputValue {
    param(
        [object]$Outputs,
        [string]$Name
    )

    $property = $Outputs.PSObject.Properties[$Name]
    if (-not $property) {
        throw "Deployment output '$Name' was not found."
    }

    return $property.Value.value
}

function Resolve-PythonCommand {
    param(
        [string]$RepoRoot
    )

    $venvCandidates = if ($IsWindows) {
        @(
            (Join-Path $RepoRoot ".venv" "Scripts" "python.exe"),
            (Join-Path $RepoRoot ".venv" "bin" "python")
        )
    }
    else {
        @(
            (Join-Path $RepoRoot ".venv" "bin" "python"),
            (Join-Path $RepoRoot ".venv" "Scripts" "python.exe")
        )
    }

    foreach ($candidate in $venvCandidates) {
        if (Test-Path -LiteralPath $candidate) {
            return (Resolve-Path -LiteralPath $candidate).Path
        }
    }

    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) {
        return $python.Source
    }

    $python3 = Get-Command python3 -ErrorAction SilentlyContinue
    if ($python3) {
        return $python3.Source
    }

    throw "Python is required to bootstrap the Search index. Use the dev container or install Python 3.12 and the repo dependencies first."
}

function Ensure-OpenAiDeployment {
    param(
        [string]$ResourceGroup,
        [string]$OpenAiName,
        [string]$DeploymentName,
        [string]$ModelName,
        [string]$ModelVersion,
        [string]$SkuName,
        [int]$Capacity
    )

    $DeploymentName = Get-RequiredValue -Value $DeploymentName -Name "OpenAI chat deployment name"

    $showOutput = & az cognitiveservices account deployment show `
        --resource-group $ResourceGroup `
        --name $OpenAiName `
        --deployment-name $DeploymentName `
        --only-show-errors `
        -o json 2>&1

    if ($LASTEXITCODE -eq 0) {
        Write-Host "OpenAI deployment already present: $DeploymentName" -ForegroundColor DarkGray
        return
    }

    $message = Convert-AzOutputToText -Output $showOutput
    if ($message -notmatch "not found|could not be found|cannot be found|DeploymentNotFound") {
        throw $message
    }

    if ([string]::IsNullOrWhiteSpace($ModelName) -or [string]::IsNullOrWhiteSpace($ModelVersion)) {
        throw "OpenAI deployment '$DeploymentName' does not exist. Fill openAiChatModelName and openAiChatModelVersion in the parameter file or create the deployment manually."
    }

    if ($Capacity -le 0) {
        throw "openAiChatCapacity must be greater than zero when the OpenAI deployment needs to be created."
    }

    $SkuName = if ([string]::IsNullOrWhiteSpace($SkuName)) { "Standard" } else { $SkuName }

    Write-Host "Creating OpenAI deployment: $DeploymentName ($ModelName $ModelVersion)" -ForegroundColor Cyan
    Invoke-AzJson -Arguments @(
        "cognitiveservices", "account", "deployment", "create",
        "--resource-group", $ResourceGroup,
        "--name", $OpenAiName,
        "--deployment-name", $DeploymentName,
        "--model-format", "OpenAI",
        "--model-name", $ModelName,
        "--model-version", $ModelVersion,
        "--sku-name", $SkuName,
        "--sku-capacity", ([string]$Capacity)
    ) | Out-Null
}

function Ensure-SearchIndex {
    param(
        [string]$RepoRoot,
        [string]$SearchEndpoint,
        [string]$IndexName,
        [string]$SearchIndexScript
    )

    $python = Resolve-PythonCommand -RepoRoot $RepoRoot
    $scriptPath = Resolve-ExistingPath -PathValue $SearchIndexScript -Name "SearchIndexScript"

    Write-Host "Ensuring Search index exists: $IndexName" -ForegroundColor Cyan
    & $python $scriptPath --endpoint $SearchEndpoint --index-name $IndexName --retries 18 --delay-seconds 10
    if ($LASTEXITCODE -ne 0) {
        throw "Search index bootstrap failed for '$IndexName'."
    }
}

function Write-Day0State {
    param(
        [string]$OutputsFile,
        [string]$Track,
        [string]$SubscriptionId,
        [string]$ResourceGroup,
        [string]$Location,
        [hashtable]$Environment,
        [hashtable]$Resources
    )

    $directory = Split-Path -Parent $OutputsFile
    if (-not [string]::IsNullOrWhiteSpace($directory) -and -not (Test-Path -LiteralPath $directory)) {
        New-Item -ItemType Directory -Path $directory -Force | Out-Null
    }

    $payload = [ordered]@{
        track = $Track
        generatedAtUtc = (Get-Date).ToUniversalTime().ToString("o")
        subscriptionId = $SubscriptionId
        resourceGroup = $ResourceGroup
        location = $Location
        environment = $Environment
        resources = $Resources
    }

    $payload | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $OutputsFile -Encoding utf8
}
