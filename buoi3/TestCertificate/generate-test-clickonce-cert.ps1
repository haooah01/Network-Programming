<# 
    Generates a self-signed code signing certificate suitable for ClickOnce testing.
    The certificate is placed in the CurrentUser\My store and exported to .pfx and .cer files.
#>

param(
    [string]$PublisherName = "Test ClickOnce Publisher",
    [string]$OutputDirectory = ".",
    [int]$ValidYears = 1,
    [SecureString]$Password
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$resolvedOutput = Resolve-Path -LiteralPath $OutputDirectory

if (-not $PSBoundParameters.ContainsKey("Password")) {
    $Password = Read-Host -Prompt "Enter password for exported PFX" -AsSecureString
}

if ($ValidYears -lt 1 -or $ValidYears -gt 10) {
    throw "ValidYears must be between 1 and 10."
}

$expiry = (Get-Date).AddYears($ValidYears)
$subject = "CN=$PublisherName"

Write-Host "Creating self-signed code signing certificate for $subject (expires $expiry)..." -ForegroundColor Cyan

$certificate = New-SelfSignedCertificate `
    -Type CodeSigning `
    -Subject $subject `
    -CertStoreLocation "Cert:\CurrentUser\My" `
    -KeyExportPolicy Exportable `
    -KeySpec Signature `
    -NotAfter $expiry `
    -HashAlgorithm "SHA256"

$safeName = ($PublisherName -replace "[^A-Za-z0-9_-]", "-").Trim("-")
if ([string]::IsNullOrWhiteSpace($safeName)) {
    $safeName = "clickonce-publisher"
}

$timestamp = Get-Date -Format "yyyyMMddHHmmss"
$baseFileName = "$safeName-$timestamp"
$pfxPath = Join-Path $resolvedOutput "$baseFileName.pfx"
$cerPath = Join-Path $resolvedOutput "$baseFileName.cer"

Export-PfxCertificate -Cert $certificate -FilePath $pfxPath -Password $Password | Out-Null
Export-Certificate -Cert $certificate -FilePath $cerPath | Out-Null

Write-Host "Certificate created:" -ForegroundColor Green
Write-Host "  Subject: $subject"
Write-Host "  Thumbprint: $($certificate.Thumbprint)"
Write-Host "  PFX: $pfxPath"
Write-Host "  CER: $cerPath"
Write-Host ""
Write-Host "Import into Visual Studio (Project > Properties > Signing) and select the exported PFX." -ForegroundColor Yellow
