# stop-server.ps1 - stops background tcp-server processes
Write-Host "Searching for tcp-server processes..."

# Find processes with tcp-server in the path
$procs = Get-Process | Where-Object { 
    $_.Path -like "*tcp-server*" -or $_.MainWindowTitle -like "*tcp-server*"
}

if ($procs.Count -eq 0) {
    Write-Host "No tcp-server processes found." -ForegroundColor Yellow
    
    # Also check for dotnet processes that might be running our server
    $dotnetProcs = Get-CimInstance Win32_Process | Where-Object { 
        $_.Name -eq 'dotnet.exe' -and $_.CommandLine -like "*tcp-server*"
    }
    
    if ($dotnetProcs) {
        Write-Host "Found dotnet processes running tcp-server:"
        foreach ($p in $dotnetProcs) {
            Write-Host "  PID $($p.ProcessId): $($p.CommandLine)"
            $confirm = Read-Host "Stop process $($p.ProcessId)? (y/n)"
            if ($confirm -eq 'y') {
                Stop-Process -Id $p.ProcessId -Force
                Write-Host "Stopped process $($p.ProcessId)" -ForegroundColor Green
            }
        }
    } else {
        Write-Host "No running tcp-server processes found."
    }
} else {
    Write-Host "Found $($procs.Count) tcp-server process(es):"
    foreach ($p in $procs) {
        Write-Host "  PID $($p.Id): $($p.ProcessName) - $($p.Path)"
    }
    
    $confirm = Read-Host "Stop all these processes? (y/n)"
    if ($confirm -eq 'y') {
        $procs | Stop-Process -Force
        Write-Host "All tcp-server processes stopped." -ForegroundColor Green
    } else {
        Write-Host "No processes stopped."
    }
}
