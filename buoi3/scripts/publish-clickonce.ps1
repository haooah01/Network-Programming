<#
    Builds the WinForms ClickOnce payload using dotnet publish,
    regenerates manifests with Mage, adjusts the entry point, and signs everything.
#>

param(
    [string]$Project = "AuthenticatedStreamClassApp/WinFormsHost/WinFormsHost.csproj",
    [string]$Configuration = "Release",
    [string]$RuntimeIdentifier = "win-x64",
    [string]$OutputDirectory = "AuthenticatedStreamClassApp/WinFormsHost/bin/Release/net8.0-windows/win-x64/publish",
    [string]$MagePath = "C:/Program Files (x86)/Microsoft SDKs/Windows/v10.0A/bin/NETFX 4.8 Tools/mage.exe",
    [string]$PfxPath = "cert/codesign.pfx",
    [string]$PfxPassword = "TempPass!234",
    [string]$Version = "1.0.0.0",
    [string]$ProductName = "WinFormsHost"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectPath = Resolve-Path -LiteralPath $Project
if (-not (Test-Path $MagePath)) { throw "mage.exe not found at '$MagePath'." }
if (-not (Test-Path $PfxPath)) { throw "PFX file not found: $PfxPath" }

$outputDir = Resolve-Path -LiteralPath (New-Item -ItemType Directory -Force -Path $OutputDirectory)

Write-Host "Publishing $Project to $($outputDir.Path) ..." -ForegroundColor Cyan
dotnet publish $projectPath `
    -c $Configuration `
    -r $RuntimeIdentifier `
    --self-contained:false `
    -p:PublishSingleFile=false `
    -p:IncludeNativeLibrariesForSelfExtract=false `
    -o $outputDir.Path | Out-String | Out-Null

$appManifestPath = Join-Path $outputDir.Path "WinFormsHost.exe.manifest"
$deployManifestPath = Join-Path $outputDir.Path "WinFormsHost.application"

Remove-Item -LiteralPath $appManifestPath, $deployManifestPath -ErrorAction SilentlyContinue

Write-Host "Generating ClickOnce application manifest with Mage..." -ForegroundColor Cyan
& $MagePath -New Application `
    -Processor amd64 `
    -Name $ProductName `
    -Version $Version `
    -FromDirectory $outputDir.Path `
    -ToFile $appManifestPath

[xml]$appManifest = Get-Content -LiteralPath $appManifestPath
$namespaceManager = New-Object System.Xml.XmlNamespaceManager($appManifest.NameTable)
$namespaceManager.AddNamespace("asmv1", "urn:schemas-microsoft-com:asm.v1")
$namespaceManager.AddNamespace("asmv2", "urn:schemas-microsoft-com:asm.v2")
$namespaceManager.AddNamespace("asmv3", "urn:schemas-microsoft-com:asm.v3")
$namespaceManager.AddNamespace("co", "urn:schemas-microsoft-com:clickonce.v1")
$namespaceManager.AddNamespace("dsig", "http://www.w3.org/2000/09/xmldsig#")

# Fix assembly identity token
$assemblyIdentityNode = $appManifest.SelectSingleNode("/asmv2:assembly/asmv1:assemblyIdentity", $namespaceManager)
if ($assemblyIdentityNode) {
    $assemblyIdentityNode.SetAttribute("publicKeyToken", "0000000000000000")
}

# Replace entryPoint with explicit commandLine
$entryPointNode = $appManifest.SelectSingleNode("/asmv2:assembly/asmv2:entryPoint", $namespaceManager)
if ($entryPointNode) { $entryPointNode.ParentNode.RemoveChild($entryPointNode) | Out-Null }
$newEntryPoint = $appManifest.CreateElement("entryPoint", "urn:schemas-microsoft-com:asm.v2")
$entryAssembly = $appManifest.CreateElement("assemblyIdentity", "urn:schemas-microsoft-com:asm.v2")
$entryAssembly.SetAttribute("name", "WinFormsHost.exe")
$entryAssembly.SetAttribute("version", $Version)
$entryAssembly.SetAttribute("language", "neutral")
$entryAssembly.SetAttribute("processorArchitecture", "amd64")
$commandLine = $appManifest.CreateElement("commandLine", "urn:schemas-microsoft-com:asm.v2")
$commandLine.SetAttribute("file", "WinFormsHost.exe")
$commandLine.SetAttribute("parameters", "")
$null = $newEntryPoint.AppendChild($entryAssembly)
$null = $newEntryPoint.AppendChild($commandLine)
$null = $appManifest.DocumentElement.InsertBefore($newEntryPoint, $appManifest.DocumentElement.SelectSingleNode("asmv2:trustInfo", $namespaceManager))

# Update dependency identity for WinFormsHost.dll
$winFormsDep = $appManifest.SelectSingleNode("//asmv2:dependentAssembly[@asmv2:codebase='WinFormsHost.dll']/asmv2:assemblyIdentity", $namespaceManager)
if ($winFormsDep) {
    $winFormsDep.SetAttribute("name", "WinFormsHost")
    $winFormsDep.SetAttribute("language", "neutral")
    $winFormsDep.SetAttribute("processorArchitecture", "msil")
    $winFormsDep.RemoveAttribute("type")
}

$appManifest.Save($appManifestPath)

Write-Host "Generating deployment manifest..." -ForegroundColor Cyan
& $MagePath -New Deployment `
    -Name $ProductName `
    -Version $Version `
    -Publisher "VSCode Internal" `
    -Install true `
    -AppManifest $appManifestPath `
    -ToFile $deployManifestPath

Write-Host "Signing manifests..." -ForegroundColor Cyan
& $MagePath -Sign $appManifestPath -CertFile (Resolve-Path $PfxPath) -Password $PfxPassword
& $MagePath -Sign $deployManifestPath -CertFile (Resolve-Path $PfxPath) -Password $PfxPassword
& $MagePath -Verify $deployManifestPath | Out-Null

Write-Host ""
Write-Host "Publish directory: $($outputDir.Path)" -ForegroundColor Green
Write-Host "Application manifest: $appManifestPath" -ForegroundColor Green
Write-Host "Deployment manifest: $deployManifestPath" -ForegroundColor Green
Write-Host "ClickOnce package generated and signed." -ForegroundColor Green
