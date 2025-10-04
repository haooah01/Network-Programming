@echo off
echo ================================
echo    TCP Chat System Launcher
echo ================================
echo.
echo Choose an option:
echo 1. Start Server
echo 2. Start Client
echo 3. Build Solution
echo 4. Exit
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo Starting TCP Chat Server...
    dotnet run --project TCPServer\TCPServer.csproj
) else if "%choice%"=="2" (
    echo Starting TCP Chat Client...
    dotnet run --project TCPClient\TCPClient.csproj
) else if "%choice%"=="3" (
    echo Building solution...
    dotnet build ChatTCP.sln
    pause
) else if "%choice%"=="4" (
    echo Goodbye!
    exit
) else (
    echo Invalid choice!
    pause
)