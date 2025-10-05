param(
    [string]$Port = "8080",
    [ValidateSet("line", "len")]
    [string]$Mode = "line",
    [switch]$KeepServer = $false
)

$root = Split-Path -Parent $PSScriptRoot
$python = if ($env:PYTHON) { $env:PYTHON } else { "python" }

$serverArgs = @(
    "`"$root/server.py`"",
    "--host", "127.0.0.1",
    "--port", $Port,
    "--mode", $Mode,
    "--timeout", "5",
    "--debug"
)

Write-Host "Starting server on port $Port (mode=$Mode)..."
$server = Start-Process -FilePath $python -ArgumentList $serverArgs -WorkingDirectory $root -PassThru
Write-Host "TCP echo connect here! Server PID=$($server.Id)"
Start-Sleep -Seconds 1

try {
    $clientArgs = @(
        "`"$root/client.py`"",
        "--host", "127.0.0.1",
        "--port", $Port,
        "--mode", $Mode,
        "--input", "inline",
        "--text", "HELLO! TCP echo connecting here!!!"
    )
    & $python @clientArgs
}
finally {
    if (-not $KeepServer) {
        if ($server -and !$server.HasExited) {
            Write-Host "Stopping server..."
            $server.CloseMainWindow() | Out-Null
            Start-Sleep -Milliseconds 300
            if (!$server.HasExited) {
                $server.Kill()
            }
        }
    }
    else {
        Write-Host "Keeping server running (PID=$($server.Id)). Connect clients to 127.0.0.1:$Port"
    }
}
