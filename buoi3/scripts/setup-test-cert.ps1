<#
    Creates a self-signed code-signing certificate for internal testing.
    Exports both PFX and CER files to the target directory and leaves the
    certificate installed in the CurrentUser\My store for immediate use.
#>

param(
    [string]$CertName = "CN=YourName-InternalTestCert",
    [string]$OutDir = "./cert",
    [string]$PfxPassword = "ChangeThis!123",
    [int]$Years = 3
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ($Years -lt 1 -or $Years -gt 10) {
    throw "Years must be between 1 and 10."
}

$resolvedOutDir = Resolve-Path -LiteralPath (New-Item -ItemType Directory -Force -Path $OutDir)

Write-Host "=> Creating self-signed code signing certificate ($CertName) ..."
$notAfter = (Get-Date).AddYears($Years)
$cert = New-SelfSignedCertificate `
    -Subject $CertName `
    -Type CodeSigningCert `
    -CertStoreLocation "Cert:\CurrentUser\My" `
    -KeyExportPolicy Exportable `
    -HashAlgorithm "SHA256" `
    -KeyLength 2048 `
    -NotAfter $notAfter

$secure = ConvertTo-SecureString -String $PfxPassword -Force -AsPlainText
$pfxPath = Join-Path $resolvedOutDir.Path "codesign.pfx"
$cerPath = Join-Path $resolvedOutDir.Path "codesign.cer"

Export-PfxCertificate -Cert $cert -FilePath $pfxPath -Password $secure | Out-Null
Export-Certificate -Cert $cert -FilePath $cerPath | Out-Null

Write-Host "OK -> $pfxPath"
Write-Host "OK -> $cerPath"
Write-Host "Thumbprint: $($cert.Thumbprint)"
Write-Host "Installed in CurrentUser\My. Inspect via certmgr.msc if needed."
