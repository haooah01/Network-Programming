# TCP Listener App

A minimal-yet-modern TCP echo server inspired by the official `TcpListener` documentation. It listens for incoming clients, echoes every message back in upper-case, supports graceful shutdown with `Ctrl+C`, and now ships with a companion sender tool for quick testing.

## Features

- Configurable bind address, port, and backlog via command-line options.
- Graceful cancellation and connection shutdown.
- Structured logging of connection lifecycle and payloads.
- Bundled sender utility to fire test messages and capture the echo.
- Tested end-to-end with integration-style xUnit tests that exercise both server and sender.

## Project Layout

```
TcpListenerApp/          # TCP echo server (net8.0)
  Program.cs            # Entry point and server implementation
  AssemblyInfo.cs       # Internal visibility for tests

TcpSenderApp/            # TCP client/sender (net8.0)
  Program.cs            # CLI for sending messages and reading responses

tests/TcpListenerApp.Tests/
  ServerTests.cs        # Integration tests covering server + sender workflow

publish/                 # Optional self-contained binaries (after `dotnet publish`)

README.md               # This file
```

## Try it

```powershell
cd "d:\Documents-D\VS Code\network programming\buoi3\TCPlistenerapp"
dotnet run --project .\TcpListenerApp -- --port 13000 --ip 127.0.0.1
```

Then, from another terminal, connect with `telnet`, `nc`, the bundled sender (below), or a custom client and type messages to see them echoed back in upper case.

### Send a message with the bundled client

Open a second terminal and run:

```powershell
cd "d:\Documents-D\VS Code\network programming\buoi3\TCPlistenerapp"
dotnet run --project .\TcpSenderApp -- --host 127.0.0.1 --port 13000 --message "hello again"
```

You should see output similar to:

```
Response: HELLO AGAIN
Elapsed: 12.4 ms
```

### One-click run on Windows

If you prefer to launch the server without typing commands, use the pre-built executable:

1. Publish (already done once during setup):

   ```powershell
  cd "d:\Documents-D\VS Code\network programming\buoi3\TCPlistenerapp"
   dotnet publish .\TcpListenerApp\TcpListenerApp.csproj -c Release -r win-x64 --self-contained false --output .\publish
   ```

2. Inside the `publish` folder, double-click `TcpListenerApp.exe` to start the listener. A console window will appear showing the bound address; close it with `Ctrl+C` when finished.

You can repeat the same publish step for the sender (replace the project path with `TcpSenderApp\TcpSenderApp.csproj`) to get a clickable `TcpSenderApp.exe` that prompts for host/port/message via command-line arguments or shortcuts.

### Command-line options

| Option | Description | Default |
|--------|-------------|---------|
| `-p`, `--port <number>` | Port to listen on. | `13000`
| `-i`, `--ip <address>`  | Local IP address to bind. | `127.0.0.1`
| `-b`, `--backlog <number>` | Maximum pending connection backlog. | `100`
| `-h`, `--help` | Print the help text. | — |

## Tests

```powershell
cd "d:\Documents-D\VS Code\network programming\buoi3\TCPlistenerapp"
dotnet test .\tests\TcpListenerApp.Tests\TcpListenerApp.Tests.csproj
```

The test spins up the listener on an ephemeral port, connects with a TCP client, and verifies the echo behavior end-to-end.

## Next steps

- Add structured logging (e.g., with `Microsoft.Extensions.Logging`).
- Support TLS via `SslStream` for secure connections.
- Accept JSON payloads and plug in a custom processing pipeline.
