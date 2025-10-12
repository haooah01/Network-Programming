<#
    Signs .exe and .dll files in a publish directory using signtool.exe.
#>

param(
    [string]$PublishDir = "./bin/Release/net8.0/win-x64/publish",
    [string]$PfxPath = "./cert/codesign.pfx",
    [string]$PfxPassword = "ChangeThis!123",
    [string]$SdkSigntool = "C:\Program Files (x86)\Windows Kits\10\bin\x64\signtool.exe",
    [string]$TimestampUrl = "http://timestamp.digicert.com"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not (Test-Path $SdkSigntool)) {
    throw "signtool.exe not found at '$SdkSigntool'. Adjust the SdkSigntool parameter."
}
if (-not (Test-Path $PfxPath)) {
    throw "PFX not found at '$PfxPath'. Run setup-test-cert.ps1 first."
}

$publishRoots = @()
$wildcardMatches = Get-ChildItem -Path $PublishDir -Directory -ErrorAction SilentlyContinue
if ($wildcardMatches) {
    $publishRoots = $wildcardMatches
} elseif (Test-Path -LiteralPath $PublishDir) {
    $publishRoots = @(Get-Item -LiteralPath $PublishDir)
} else {
    throw "Publish directory pattern '$PublishDir' matched nothing."
}

$filesToSign = @()
foreach ($root in $publishRoots) {
    $filesToSign += Get-ChildItem -Path $root.FullName -Include *.exe,*.dll -File -Recurse
}

if ($filesToSign.Count -eq 0) {
    Write-Host "No binaries found to sign under $PublishDir."
    exit 0
}

foreach ($file in $filesToSign) {
    Write-Host "Signing $($file.FullName)"
    & "$SdkSigntool" sign `
        /f "$PfxPath" `
        /p "$PfxPassword" `
        /fd sha256 `
        /tr "$TimestampUrl" `
        /td sha256 `
        "$($file.FullName)"
}

Write-Host "Done signing $($filesToSign.Count) file(s)."
