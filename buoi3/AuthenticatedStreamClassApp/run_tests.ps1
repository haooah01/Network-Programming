# Simple test runner script for the demo
$project = Get-Location
Write-Host "Running demo without client cert"
cd $project
dotnet run --project . -- --port 0
$code1 = $LASTEXITCODE
Write-Host "Run 1 exit code: $code1"

Write-Host "Running demo with mutual TLS"
cd $project
dotnet run --project . -- --port 0 --requireClientCert
$code2 = $LASTEXITCODE
Write-Host "Run 2 exit code: $code2"

if ($code1 -eq 0 -and $code2 -eq 0) { Write-Host "Both runs succeeded"; exit 0 } else { Write-Host "One or more runs failed"; exit 1 }
