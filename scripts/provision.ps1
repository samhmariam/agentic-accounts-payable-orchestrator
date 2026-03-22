[CmdletBinding(PositionalBinding = $false)]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$RemainingArgs
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Warning "scripts/provision.ps1 now aliases the recommended core bootstrap. Use scripts/provision-full.ps1 for the optional full platform track."
& (Join-Path $PSScriptRoot "provision-core.ps1") @RemainingArgs
exit $LASTEXITCODE
