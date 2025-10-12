<#
    Signs ClickOnce application and deployment manifests using mage.exe.
#>

param(
    [string]$AppManifest = "./bin/Release/net8.0-windows/win-x64/publish/MyApp.exe.manifest",
    [string]$DeployManifest = "./bin/Release/net8.0-windows/win-x64/publish/MyApp.application",
    [string]$PfxPath = "./cert/codesign.pfx",
    [string]$PfxPassword = "ChangeThis!123",
    [string]$MagePath = "C:\Program Files (x86)\Microsoft SDKs\Windows\v10.0A\bin\NETFX 4.8 Tools\mage.exe"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not (Test-Path $MagePath)) {
    throw "mage.exe not found at '$MagePath'. Adjust the MagePath parameter."
}
if (-not (Test-Path $PfxPath)) {
    throw "PFX not found at '$PfxPath'. Run setup-test-cert.ps1 first."
}

function Resolve-SingleFile {
    param(
        [string]$Pattern,
        [string]$Description
    )

    $matches = @(Get-ChildItem -Path $Pattern -File -ErrorAction SilentlyContinue)
    if (-not $matches) {
        if (Test-Path -LiteralPath $Pattern) {
            return Get-Item -LiteralPath $Pattern
        }
        throw "$Description not found: $Pattern"
    }
    if ($matches.Count -gt 1) {
        throw "$Description pattern '$Pattern' matched more than one file. Please provide a more specific path."
    }
    return $matches[0]
}

$appManifestFile = Resolve-SingleFile -Pattern $AppManifest -Description "App manifest"
$deployManifestFile = Resolve-SingleFile -Pattern $DeployManifest -Description "Deploy manifest"

Write-Host "Signing application manifest: $($appManifestFile.FullName)"
& "$MagePath" -Sign "$($appManifestFile.FullName)" -CertFile "$PfxPath" -Password "$PfxPassword"

Write-Host "Signing deployment manifest: $($deployManifestFile.FullName)"
& "$MagePath" -Sign "$($deployManifestFile.FullName)" -CertFile "$PfxPath" -Password "$PfxPassword"

Write-Host "ClickOnce manifests signed successfully."
