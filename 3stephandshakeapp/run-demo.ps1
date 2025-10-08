# run-demo.ps1 - builds projects, launches server in new window, waits for server_port.txt, runs client
param(
    [int]$WaitSeconds = 10
)

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Write-Host "Workspace root: $root"

# Build both projects
Write-Host "Building server..."
cd (Join-Path $root 'tcp-server')
dotnet build | Write-Host
Write-Host "Building client..."
cd (Join-Path $root 'tcp-client')
dotnet build | Write-Host

Write-Host "Starting server in background and capturing its stdout..."

# Start the server process and capture stdout
$serverExe = 'dotnet'
$serverArgs = 'run'
$si = New-Object System.Diagnostics.ProcessStartInfo
$si.FileName = $serverExe
$si.WorkingDirectory = (Join-Path $root 'tcp-server')
$si.Arguments = $serverArgs
$si.RedirectStandardOutput = $true
$si.RedirectStandardError = $true
$si.UseShellExecute = $false
$si.CreateNoWindow = $true

$p = New-Object System.Diagnostics.Process
$p.StartInfo = $si
$p.Start() | Out-Null

# Read lines from stdout until we find the JSON ports line
$portObj = $null
$start = Get-Date
while ((Get-Date) - $start -lt [TimeSpan]::FromSeconds($WaitSeconds)) {
    if ($p.HasExited) { Write-Host "Server process exited unexpectedly." -ForegroundColor Red; $err = $p.StandardError.ReadToEnd(); Write-Host $err; exit 1 }
    while (-not $p.StandardOutput.EndOfStream) {
        $line = $p.StandardOutput.ReadLine()
        Write-Host "[server] $line"
        try {
            $maybe = $line | ConvertFrom-Json -ErrorAction SilentlyContinue
            if ($maybe -and $maybe.port) { $portObj = $maybe; break }
        } catch {
        }
    }
    if ($portObj) { break }
    Start-Sleep -Milliseconds 200
}

if (-not $portObj) { Write-Host "Failed to read ports from server stdout within timeout." -ForegroundColor Red; exit 1 }

$port = $portObj.port
$uiPort = $portObj.ui
Write-Host "Server reported ports: tcp=$port ui=$uiPort"

Write-Host "Running client against 127.0.0.1:$port"
cd (Join-Path $root 'tcp-client')
dotnet run 127.0.0.1 $port | Write-Host

if ($uiPort -and $uiPort -gt 0) {
    Start-Process "http://localhost:$uiPort/"
    Write-Host "Opened UI at http://localhost:$uiPort/"
}

Write-Host "Demo complete. Server is running in background; check server stdout above or close the host process to stop."
