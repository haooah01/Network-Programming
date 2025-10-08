# TCP Client Demo Test Script
# This script demonstrates all features of the TcpClient application

Write-Host "=== TCP Client Class Application Test ===" -ForegroundColor Green
Write-Host "`nThis script will test all TcpClient features with the server.`n" -ForegroundColor Yellow

# Build the solution
Write-Host "Step 1: Building the solution..." -ForegroundColor Cyan
dotnet build
if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed!" -ForegroundColor Red
    exit 1
}
Write-Host "Build successful!`n" -ForegroundColor Green

# Start the server
Write-Host "Step 2: Starting TCP Server..." -ForegroundColor Cyan
$serverJob = Start-Job -ScriptBlock {
    Set-Location "d:\Documents-D\VS Code\network programming\TCPclientclassapp"
    dotnet run --project TcpServer
}
Start-Sleep -Seconds 2
Write-Host "Server started (Job ID: $($serverJob.Id))`n" -ForegroundColor Green

# Test 1: Simple Connect
Write-Host "Test 1: Simple Connect and Send" -ForegroundColor Cyan
Write-Host "----------------------------------------"
$output = @"
1
Hello from PowerShell!

"@ | dotnet run --project TcpClientDemo
Write-Host $output
Write-Host ""

Start-Sleep -Seconds 1

# Test 2: Multiple Messages
Write-Host "Test 2: Multiple Messages" -ForegroundColor Cyan
Write-Host "----------------------------------------"
$output = @"
2
First message
Second message
TCP rocks!
quit

"@ | dotnet run --project TcpClientDemo
Write-Host $output
Write-Host ""

Start-Sleep -Seconds 1

# Test 3: Connection Properties
Write-Host "Test 3: Check Connection Properties" -ForegroundColor Cyan
Write-Host "----------------------------------------"
$output = @"
3

"@ | dotnet run --project TcpClientDemo
Write-Host $output
Write-Host ""

Start-Sleep -Seconds 1

# Test 4: Async Connect
Write-Host "Test 4: Async Connect Demo" -ForegroundColor Cyan
Write-Host "----------------------------------------"
$output = @"
4

"@ | dotnet run --project TcpClientDemo
Write-Host $output
Write-Host ""

# Stop the server
Write-Host "Stopping server..." -ForegroundColor Cyan
Stop-Job -Job $serverJob
Remove-Job -Job $serverJob
Write-Host "Server stopped.`n" -ForegroundColor Green

Write-Host "=== All Tests Completed ===" -ForegroundColor Green
Write-Host "`nTo run manually:" -ForegroundColor Yellow
Write-Host "1. Terminal 1: dotnet run --project TcpServer" -ForegroundColor White
Write-Host "2. Terminal 2: dotnet run --project TcpClientDemo" -ForegroundColor White
