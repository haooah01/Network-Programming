# TCP Client Class - Live Demo

## Quick Start Guide

### Option 1: Using Batch File (Easiest)
```cmd
cd TCPclientclassapp
run-demo.bat
```
This will open **two command windows** automatically:
- Window 1: TCP Server
- Window 2: TCP Client Demo

### Option 2: Manual (Two Terminals)

**Terminal 1 - Server:**
```powershell
cd TCPclientclassapp
dotnet run --project TcpServer
```

**Terminal 2 - Client:**
```powershell
cd TCPclientclassapp
dotnet run --project TcpClientDemo
```

---

## Demo Scenarios

### 📋 Scenario 1: Simple Connect and Send

**What it demonstrates:**
- Basic TcpClient connection
- Sending ASCII-encoded messages
- Receiving server response
- Proper resource disposal with `using` statement

**Steps:**
1. Run the client
2. Select option `1`
3. Enter a message: `Hello World!`
4. Press Enter

**Expected Result:**
```
Sent: Hello World!
Received: HELLO WORLD!
```

**Server will show:**
```
Client #1 connected: 127.0.0.1:xxxxx
Received: Hello World!
Sent: HELLO WORLD!
Client #1 disconnected.
```

---

### 📋 Scenario 2: Multiple Messages

**What it demonstrates:**
- Persistent TCP connection
- Sending multiple messages without reconnecting
- Interactive chat-like communication

**Steps:**
1. Select option `2`
2. Type several messages:
   - `Hello`
   - `This is message 2`
   - `TCP is awesome!`
   - `quit` (to exit)

**Expected Result:**
```
Connected to 127.0.0.1:13000
Enter messages (type 'quit' to exit):

> Hello
Server: HELLO

> This is message 2
Server: THIS IS MESSAGE 2

> TCP is awesome!
Server: TCP IS AWESOME!

> quit
```

**Server will show:**
```
Client #2 connected: 127.0.0.1:xxxxx
Received: Hello
Sent: HELLO
Received: This is message 2
Sent: THIS IS MESSAGE 2
Received: TCP is awesome!
Sent: TCP IS AWESOME!
Client #2 disconnected.
```

---

### 📋 Scenario 3: Connection Properties

**What it demonstrates:**
- TcpClient configuration properties
- Connection state inspection
- Buffer sizes and timeout values
- Underlying Socket details (endpoints, protocols)

**Steps:**
1. Select option `3`
2. Press Enter to continue

**Expected Result:**
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

Test message response: PROPERTY TEST
```

**Key Observations:**
- `Connected` changes from `False` to `True` after connection
- Default buffer sizes are 64KB (65536 bytes)
- Timeouts are 0 (infinite)
- LocalEndPoint shows ephemeral port assigned by OS
- RemoteEndPoint confirms connection to 127.0.0.1:13000

---

### 📋 Scenario 4: Async Connect

**What it demonstrates:**
- Asynchronous connection using `ConnectAsync()`
- Non-blocking I/O operations
- `async/await` pattern with `WriteAsync()` and `ReadAsync()`

**Steps:**
1. Select option `4`
2. Press Enter to continue

**Expected Result:**
```
Async connecting to 127.0.0.1:13000...
Connected asynchronously!
Sent: Async Hello!
Received: ASYNC HELLO!
```

**Why it matters:**
- Non-blocking: UI remains responsive during connection
- Scalability: Can handle many concurrent connections
- Modern pattern: Recommended for production applications

---

## Code Walkthrough

### TcpClient Construction
```csharp
// Constructor connects immediately
using TcpClient client = new TcpClient(server, port);
```

### Sending Data
```csharp
// Convert string to bytes
Byte[] data = System.Text.Encoding.ASCII.GetBytes(message);

// Get network stream
NetworkStream stream = client.GetStream();

// Send data
stream.Write(data, 0, data.Length);
```

### Receiving Data
```csharp
// Buffer for incoming data
data = new Byte[256];

// Read from stream
Int32 bytes = stream.Read(data, 0, data.Length);

// Convert bytes to string
String responseData = System.Text.Encoding.ASCII.GetString(data, 0, bytes);
```

### Async Pattern
```csharp
// Async connection
await client.ConnectAsync(server, port);

// Async write
await stream.WriteAsync(data, 0, data.Length);

// Async read
Int32 bytes = await stream.ReadAsync(data, 0, data.Length);
```

---

## Server Behavior

The echo server performs the following:
1. **Listen** on `127.0.0.1:13000`
2. **Accept** incoming client connections (one at a time)
3. **Receive** message (up to 256 bytes)
4. **Transform** message to UPPERCASE
5. **Send** response back to client
6. **Repeat** until client disconnects

**Server Code Snippet:**
```csharp
TcpListener server = new TcpListener(localAddr, port);
server.Start();

while (true)
{
    TcpClient client = server.AcceptTcpClient();
    NetworkStream stream = client.GetStream();
    
    // Read-Transform-Write loop
    while ((bytesRead = stream.Read(buffer, 0, buffer.Length)) > 0)
    {
        string received = Encoding.ASCII.GetString(buffer, 0, bytesRead);
        string response = received.ToUpper();
        byte[] responseBytes = Encoding.ASCII.GetBytes(response);
        stream.Write(responseBytes, 0, responseBytes.Length);
    }
}
```

---

## Architecture Diagram

```
┌─────────────────────┐                  ┌─────────────────────┐
│   TCP Client        │                  │   TCP Server        │
│   (Port: Random)    │                  │   (Port: 13000)     │
└──────────┬──────────┘                  └──────────┬──────────┘
           │                                        │
           │  1. Connect Request                    │
           │───────────────────────────────────────>│
           │                                        │
           │  2. Connection Established (3-way)     │
           │<───────────────────────────────────────│
           │                                        │
           │  3. Send: "Hello World!"               │
           │───────────────────────────────────────>│
           │                                        │
           │                                        │  [Convert to
           │                                        │   uppercase]
           │                                        │
           │  4. Receive: "HELLO WORLD!"            │
           │<───────────────────────────────────────│
           │                                        │
           │  5. Close Connection (FIN)             │
           │───────────────────────────────────────>│
           │                                        │
           │  6. Acknowledge Close (FIN-ACK)        │
           │<───────────────────────────────────────│
           │                                        │
```

---

## Learning Points

### 1. **TcpClient vs Socket**
- `TcpClient` is a high-level wrapper around `Socket`
- Simpler API for common TCP scenarios
- Automatically handles connection setup
- Provides `NetworkStream` for easy data access

### 2. **NetworkStream**
- Stream-based API for reading/writing data
- Supports both sync and async operations
- Can be used with `StreamReader`/`StreamWriter`
- Implements `IDisposable` for proper cleanup

### 3. **Resource Management**
- Always use `using` statement or `Dispose()` method
- Closing `TcpClient` automatically closes underlying `Socket`
- Closing `NetworkStream` is optional (handled by TcpClient)

### 4. **Encoding**
- ASCII: 1 byte per character (English only)
- UTF-8: Variable bytes (supports all languages)
- Always use same encoding on both sides!

### 5. **Buffer Size**
- Default: 256 bytes in examples
- Production: Often 4KB - 8KB
- Consider message size vs performance
- Can be configured via `ReceiveBufferSize` and `SendBufferSize`

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Connection refused" | Start server first! |
| "Port already in use" | Only one server per port |
| Message cut off | Increase buffer size |
| Characters corrupted | Check encoding (ASCII vs UTF-8) |
| Client hangs on Read() | Server must send data |
| Server hangs on AcceptTcpClient() | Normal - waiting for connection |

---

## Performance Tips

1. **Reuse connections** - Don't create new TcpClient for each message
2. **Use async methods** - Better scalability with many clients
3. **Buffer appropriately** - Balance memory vs syscalls
4. **Disable Nagle** - Set `NoDelay = true` for low-latency apps
5. **Set timeouts** - Prevent hanging on network issues

---

## Next Steps

After mastering this demo, explore:
- **UDP Sockets** - Connectionless protocol
- **SSL/TLS** - Secure communication with `SslStream`
- **WebSockets** - Full-duplex HTTP upgrade
- **HTTP Clients** - `HttpClient` for REST APIs
- **SignalR** - Real-time web with .NET

---

## References

- [TcpClient Class - Microsoft Docs](https://learn.microsoft.com/en-us/dotnet/api/system.net.sockets.tcpclient)
- [TcpListener Class - Microsoft Docs](https://learn.microsoft.com/en-us/dotnet/api/system.net.sockets.tcplistener)
- [NetworkStream Class - Microsoft Docs](https://learn.microsoft.com/en-us/dotnet/api/system.net.sockets.networkstream)
- [TCP Protocol - RFC 793](https://www.rfc-editor.org/rfc/rfc793)

---

**Happy Coding! 🚀**
