@echo off
REM TCP Client Demo Quick Start Script
REM This script opens two terminals: one for server, one for client

echo === TCP Client Class Application ===
echo.
echo This will open TWO command windows:
echo   1. TCP Server (port 13000)
echo   2. TCP Client Demo (interactive menu)
echo.
echo Press any key to continue...
pause > nul

REM Start server in new window
start "TCP Server" cmd /k "cd /d %~dp0 && dotnet run --project TcpServer"

REM Wait for server to start
timeout /t 2 /nobreak > nul

REM Start client in new window
start "TCP Client Demo" cmd /k "cd /d %~dp0 && dotnet run --project TcpClientDemo"

echo.
echo Both windows have been opened!
echo Close this window when done testing.
echo.
pause
