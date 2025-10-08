# TCP Client Class Application

## Overview

This project demonstrates the **Microsoft TcpClient Class** from the `System.Net.Sockets` namespace. It provides comprehensive examples based on official Microsoft documentation showing how to:

- Create TCP client connections
- Send and receive data over the network
- Handle multiple messages on a persistent connection
- Inspect connection properties
- Use asynchronous connection methods

## Project Structure

```
TCPclientclassapp/
├── TcpClientExamples.sln       # Solution file
├── TcpServer/
│   └── Program.cs              # TCP Echo Server (listens on port 13000)
├── TcpClientDemo/
│   └── Program.cs              # TCP Client with multiple examples
└── README.md                   # This file
```

## Requirements

- **.NET 8.0 SDK** or higher
- **Windows, macOS, or Linux**
- Port **13000** available on localhost

## How to Build

### Build the entire solution:
```powershell
cd TCPclientclassapp
dotnet build
```

### Build individual projects:
```powershell
# Build server
dotnet build TcpServer/TcpServer.csproj

# Build client
dotnet build TcpClientDemo/TcpClientDemo.csproj
```

## How to Run

### Step 1: Start the Server

Open a terminal and run:
```powershell
cd TCPclientclassapp
dotnet run --project TcpServer
```

**Expected output:**
```
=== TCP Echo Server ===
Listening on 127.0.0.1:13000
Waiting for connections...
```

### Step 2: Start the Client

Open a **second terminal** and run:
```powershell
cd TCPclientclassapp
dotnet run --project TcpClientDemo
```

**Expected output:**
```
=== TCP Client Demo ===
Based on Microsoft TcpClient Class Documentation

Choose an option:
1. Simple Connect and Send
2. Multiple Messages
3. Check Connection Properties
4. Async Connect Demo
5. Exit

Your choice:
```

## Features

### 1. Simple Connect and Send
- **Based on:** Microsoft Documentation `Connect()` example
- **What it does:** 
  - Creates a `TcpClient` connected to `127.0.0.1:13000`
  - Sends a user-entered message
  - Receives the server's response (echoed in uppercase)
  - Demonstrates proper resource disposal with `using` statement

**Example:**
```
Your choice: 1
Enter message to send: Hello World
Sent: Hello World
Received: HELLO WORLD
```

### 2. Multiple Messages
- **What it does:**
  - Maintains a persistent connection
  - Allows sending multiple messages without reconnecting
  - Type 'quit' to exit

**Example:**
```
Your choice: 2
Connected to 127.0.0.1:13000
Enter messages (type 'quit' to exit):

> Hello
Server: HELLO

> TCP is awesome
Server: TCP IS AWESOME

> quit
```

### 3. Check Connection Properties
- **What it does:**
  - Displays all TcpClient properties
  - Shows connection status, buffer sizes, timeouts
  - Reveals underlying Socket information (endpoints, address family, protocol)

**Example output:**
```
=== TcpClient Properties ===
Connected: False
ExclusiveAddressUse: True

Connecting to 127.0.0.1:13000...
Connected: True
Available bytes: 0
ReceiveBufferSize: 65536 bytes
SendBufferSize: 65536 bytes
ReceiveTimeout: 0 ms
SendTimeout: 0 ms
NoDelay (Nagle's algorithm disabled): False

Underlying Socket:
  LocalEndPoint: 127.0.0.1:54321
  RemoteEndPoint: 127.0.0.1:13000
  AddressFamily: InterNetwork
  SocketType: Stream
  ProtocolType: Tcp
```

### 4. Async Connect Demo
- **What it does:**
  - Demonstrates `ConnectAsync()` for non-blocking connection
  - Uses `async/await` pattern with `WriteAsync()` and `ReadAsync()`

**Example:**
```
Your choice: 4
Async connecting to 127.0.0.1:13000...
Connected asynchronously!
Sent: Async Hello!
Received: ASYNC HELLO!
```

## Code Highlights

### TcpClient Constructor
```csharp
// Connect to server immediately
using TcpClient client = new TcpClient(server, port);
```

### Sending Data
```csharp
Byte[] data = System.Text.Encoding.ASCII.GetBytes(message);
NetworkStream stream = client.GetStream();
stream.Write(data, 0, data.Length);
```

### Receiving Data
```csharp
data = new Byte[256];
Int32 bytes = stream.Read(data, 0, data.Length);
String responseData = System.Text.Encoding.ASCII.GetString(data, 0, bytes);
```

### Async Pattern
```csharp
await client.ConnectAsync(server, port);
await stream.WriteAsync(data, 0, data.Length);
Int32 bytes = await stream.ReadAsync(data, 0, data.Length);
```

## Server Behavior

The **TcpServer** project implements a simple echo server:
- Listens on `127.0.0.1:13000`
- Accepts client connections sequentially
- Receives messages up to 256 bytes
- Responds with the message converted to **UPPERCASE**
- Logs each connection with a client counter

**Server output example:**
```
=== TCP Echo Server ===
Listening on 127.0.0.1:13000
Waiting for connections...

Client #1 connected: 127.0.0.1:54321
Received: Hello World
Sent: HELLO WORLD
Client #1 disconnected.
```

## Exception Handling

The code demonstrates proper exception handling:
- **ArgumentNullException:** Invalid parameters
- **SocketException:** Network errors (connection refused, timeout, etc.)
- **General Exception:** Catch-all for unexpected errors

## Resource Management

Both server and client use proper resource disposal:
```csharp
using TcpClient client = new TcpClient(server, port);
// Automatic disposal when scope exits
```

Alternatively, manual cleanup:
```csharp
try
{
    TcpClient client = new TcpClient(server, port);
    // ... use client ...
}
finally
{
    client?.Close();
}
```

## Troubleshooting

### "Connection refused" error
- Make sure the **TcpServer** is running first
- Check if port 13000 is available (not blocked by firewall)

### "Address already in use"
- Another instance of TcpServer might be running
- Wait a few seconds for the port to be released
- Change the port number in both server and client

### Messages not received
- Ensure both server and client are using the same encoding (ASCII)
- Check buffer size (256 bytes default)

## References

- [Microsoft TcpClient Class Documentation](https://learn.microsoft.com/en-us/dotnet/api/system.net.sockets.tcpclient)
- [Microsoft TcpListener Class Documentation](https://learn.microsoft.com/en-us/dotnet/api/system.net.sockets.tcplistener)
- [NetworkStream Class Documentation](https://learn.microsoft.com/en-us/dotnet/api/system.net.sockets.networkstream)

## License

This project is based on Microsoft documentation examples and is provided for educational purposes.

---

**Author:** Generated based on Microsoft .NET documentation  
**Framework:** .NET 8.0  
**Language:** C#
