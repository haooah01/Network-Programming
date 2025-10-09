(The file `d:\Documents-D\VS Code\network programming\buoi3\AuthenticatedStreamClassApp\README.md` exists, but is empty)
AuthenticatedStreamClassApp

This is a small .NET console demo that creates an SslStream server and client running locally and prints AuthenticatedStream properties (IsAuthenticated, IsMutuallyAuthenticated, IsEncrypted, IsSigned, IsServer).

How to run (Windows PowerShell):

# build
dotnet build

# run
dotnet run --project .

Notes:
- The server uses a self-signed certificate created at runtime. The client accepts it for demo purposes.
- This app targets .NET 8.0; change the TargetFramework in the .csproj if you need a different version.

