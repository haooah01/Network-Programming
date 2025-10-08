# TcpClient Code Reference

This document contains all key code snippets from the project for quick reference.

---

## 1. Basic TcpClient Connection

```csharp
using System;
using System.Net.Sockets;
using System.Text;

// Create a TcpClient and connect to server
string server = "127.0.0.1";
int port = 13000;

using TcpClient client = new TcpClient(server, port);

// The client is now connected and ready to send/receive data
```

---

## 2. Sending Data

```csharp
// Prepare message
string message = "Hello Server!";

// Convert string to byte array using ASCII encoding
Byte[] data = Encoding.ASCII.GetBytes(message);

// Get the network stream
NetworkStream stream = client.GetStream();

// Send the data
stream.Write(data, 0, data.Length);

Console.WriteLine("Sent: {0}", message);
```

---

## 3. Receiving Data

```csharp
// Buffer to store received bytes
Byte[] data = new Byte[256];

// Read data from stream
Int32 bytes = stream.Read(data, 0, data.Length);

// Convert bytes back to string
String responseData = Encoding.ASCII.GetString(data, 0, bytes);

Console.WriteLine("Received: {0}", responseData);
```

---

## 4. Complete Client Example (Microsoft Pattern)

```csharp
static void Connect(String server, String message)
{
    try
    {
        Int32 port = 13000;
        
        // Create TcpClient with connection
        using TcpClient client = new TcpClient(server, port);

        // Convert message to bytes
        Byte[] data = Encoding.ASCII.GetBytes(message);

        // Get stream for communication
        NetworkStream stream = client.GetStream();

        // Send message
        stream.Write(data, 0, data.Length);
        Console.WriteLine("Sent: {0}", message);

        // Receive response
        data = new Byte[256];
        String responseData = String.Empty;
        Int32 bytes = stream.Read(data, 0, data.Length);
        responseData = Encoding.ASCII.GetString(data, 0, bytes);
        Console.WriteLine("Received: {0}", responseData);

        // Automatic cleanup via 'using'
    }
    catch (ArgumentNullException e)
    {
        Console.WriteLine("ArgumentNullException: {0}", e);
    }
    catch (SocketException e)
    {
        Console.WriteLine("SocketException: {0}", e);
    }
}
```

---

## 5. Async Connection Pattern

```csharp
static async Task AsyncConnectDemo()
{
    string server = "127.0.0.1";
    Int32 port = 13000;

    try
    {
        using TcpClient client = new TcpClient();
        
        // Non-blocking connection
        await client.ConnectAsync(server, port);
        Console.WriteLine("Connected asynchronously!");

        NetworkStream stream = client.GetStream();
        string message = "Async Hello!";
        
        // Async write
        Byte[] data = Encoding.ASCII.GetBytes(message);
        await stream.WriteAsync(data, 0, data.Length);
        Console.WriteLine("Sent: {0}", message);

        // Async read
        data = new Byte[256];
        Int32 bytes = await stream.ReadAsync(data, 0, data.Length);
        string response = Encoding.ASCII.GetString(data, 0, bytes);
        Console.WriteLine("Received: {0}", response);
    }
    catch (Exception e)
    {
        Console.WriteLine("Exception: {0}", e.Message);
    }
}
```

---

## 6. Multiple Messages (Persistent Connection)

```csharp
static void MultipleMessages()
{
    string server = "127.0.0.1";
    Int32 port = 13000;

    try
    {
        using TcpClient client = new TcpClient(server, port);
        NetworkStream stream = client.GetStream();

        Console.WriteLine("Connected. Enter messages (type 'quit' to exit):");

        while (true)
        {
            Console.Write("> ");
            string message = Console.ReadLine();

            if (message?.ToLower() == "quit")
                break;

            // Send message
            Byte[] data = Encoding.ASCII.GetBytes(message);
            stream.Write(data, 0, data.Length);

            // Receive response
            data = new Byte[256];
            Int32 bytes = stream.Read(data, 0, data.Length);
            string response = Encoding.ASCII.GetString(data, 0, bytes);
            Console.WriteLine("Server: {0}", response);
        }
    }
    catch (Exception e)
    {
        Console.WriteLine("Exception: {0}", e.Message);
    }
}
```

---

## 7. Check Connection Properties

```csharp
static void CheckProperties()
{
    using TcpClient client = new TcpClient();
    
    Console.WriteLine("Before connection:");
    Console.WriteLine("  Connected: {0}", client.Connected);
    
    client.Connect("127.0.0.1", 13000);
    
    Console.WriteLine("\nAfter connection:");
    Console.WriteLine("  Connected: {0}", client.Connected);
    Console.WriteLine("  Available: {0} bytes", client.Available);
    Console.WriteLine("  ReceiveBufferSize: {0}", client.ReceiveBufferSize);
    Console.WriteLine("  SendBufferSize: {0}", client.SendBufferSize);
    Console.WriteLine("  ReceiveTimeout: {0} ms", client.ReceiveTimeout);
    Console.WriteLine("  SendTimeout: {0} ms", client.SendTimeout);
    Console.WriteLine("  NoDelay: {0}", client.NoDelay);
    
    if (client.Client != null)
    {
        Console.WriteLine("\nSocket info:");
        Console.WriteLine("  LocalEndPoint: {0}", client.Client.LocalEndPoint);
        Console.WriteLine("  RemoteEndPoint: {0}", client.Client.RemoteEndPoint);
    }
}
```

---

## 8. TcpListener (Server Side)

```csharp
using System;
using System.Net;
using System.Net.Sockets;
using System.Text;

static void StartServer()
{
    IPAddress localAddr = IPAddress.Parse("127.0.0.1");
    int port = 13000;
    
    TcpListener server = null;
    try
    {
        // Create and start listener
        server = new TcpListener(localAddr, port);
        server.Start();
        Console.WriteLine("Server started on {0}:{1}", localAddr, port);

        // Main accept loop
        while (true)
        {
            Console.WriteLine("Waiting for connection...");
            
            // Blocking call - waits for client
            TcpClient client = server.AcceptTcpClient();
            Console.WriteLine("Client connected!");

            // Get network stream
            NetworkStream stream = client.GetStream();

            // Read-Write loop
            Byte[] buffer = new Byte[256];
            int bytesRead;
            
            while ((bytesRead = stream.Read(buffer, 0, buffer.Length)) > 0)
            {
                // Convert received bytes to string
                string received = Encoding.ASCII.GetString(buffer, 0, bytesRead);
                Console.WriteLine("Received: {0}", received);

                // Process and send response
                string response = received.ToUpper();
                Byte[] responseBytes = Encoding.ASCII.GetBytes(response);
                stream.Write(responseBytes, 0, responseBytes.Length);
                Console.WriteLine("Sent: {0}", response);
            }

            // Client disconnected
            client.Close();
            Console.WriteLine("Client disconnected.");
        }
    }
    catch (SocketException e)
    {
        Console.WriteLine("SocketException: {0}", e);
    }
    finally
    {
        // Stop listening
        server?.Stop();
    }
}
```

---

## 9. Exception Handling Pattern

```csharp
try
{
    using TcpClient client = new TcpClient(server, port);
    // ... your code ...
}
catch (ArgumentNullException e)
{
    // Server name is null
    Console.WriteLine("Invalid server address: {0}", e.Message);
}
catch (SocketException e)
{
    // Connection failed, timeout, refused, etc.
    Console.WriteLine("Socket error: {0}", e.Message);
    Console.WriteLine("Error code: {0}", e.ErrorCode);
}
catch (InvalidOperationException e)
{
    // TcpClient already connected
    Console.WriteLine("Invalid operation: {0}", e.Message);
}
catch (Exception e)
{
    // Catch-all for unexpected errors
    Console.WriteLine("Unexpected error: {0}", e.Message);
}
```

---

## 10. Resource Cleanup Patterns

### Pattern 1: Using Statement (Recommended)
```csharp
using TcpClient client = new TcpClient(server, port);
// client.Dispose() called automatically at end of scope
```

### Pattern 2: Using Block
```csharp
using (TcpClient client = new TcpClient(server, port))
{
    // Use client
} // client.Dispose() called here
```

### Pattern 3: Try-Finally
```csharp
TcpClient client = null;
try
{
    client = new TcpClient(server, port);
    // Use client
}
finally
{
    client?.Close(); // or client?.Dispose();
}
```

---

## 11. StreamReader/StreamWriter Wrapper

```csharp
using TcpClient client = new TcpClient(server, port);
using NetworkStream stream = client.GetStream();
using StreamReader reader = new StreamReader(stream);
using StreamWriter writer = new StreamWriter(stream);

// Write text line
writer.WriteLine("Hello Server!");
writer.Flush(); // Important!

// Read text line
string response = reader.ReadLine();
Console.WriteLine("Response: {0}", response);
```

---

## 12. Configuring TcpClient Properties

```csharp
TcpClient client = new TcpClient();

// Set buffer sizes (bytes)
client.ReceiveBufferSize = 8192;
client.SendBufferSize = 8192;

// Set timeouts (milliseconds, 0 = infinite)
client.ReceiveTimeout = 5000; // 5 seconds
client.SendTimeout = 5000;

// Disable Nagle's algorithm for low latency
client.NoDelay = true;

// Use exclusive address (prevent address reuse)
client.ExclusiveAddressUse = true;

// Now connect
client.Connect(server, port);
```

---

## 13. Check Data Available Before Reading

```csharp
using TcpClient client = new TcpClient(server, port);
NetworkStream stream = client.GetStream();

// Check if data is available to read
if (client.Available > 0)
{
    Byte[] data = new Byte[client.Available];
    int bytes = stream.Read(data, 0, data.Length);
    string message = Encoding.ASCII.GetString(data, 0, bytes);
    Console.WriteLine("Received: {0}", message);
}
else
{
    Console.WriteLine("No data available.");
}
```

---

## 14. Separate Connect and Data Transfer

```csharp
// Create without connecting
TcpClient client = new TcpClient();

try
{
    // Connect later
    client.Connect("127.0.0.1", 13000);
    
    if (client.Connected)
    {
        // Now send data
        NetworkStream stream = client.GetStream();
        // ... send/receive ...
    }
}
finally
{
    client.Close();
}
```

---

## 15. UTF-8 Encoding (for international text)

```csharp
// Use UTF-8 instead of ASCII for full Unicode support
string message = "Hello 世界!";

// Send with UTF-8
Byte[] data = Encoding.UTF8.GetBytes(message);
stream.Write(data, 0, data.Length);

// Receive with UTF-8
data = new Byte[256];
Int32 bytes = stream.Read(data, 0, data.Length);
string received = Encoding.UTF8.GetString(data, 0, bytes);
```

---

## Common Encodings Comparison

| Encoding | Bytes/Char | Languages | Use Case |
|----------|------------|-----------|----------|
| ASCII | 1 | English only | Simple text, older protocols |
| UTF-8 | 1-4 | All | Modern apps, web, JSON |
| UTF-16 | 2-4 | All | Windows internals, .NET strings |
| UTF-32 | 4 | All | Fixed-width processing |

---

## Quick Reference Cheat Sheet

```csharp
// Connect
using TcpClient client = new TcpClient("127.0.0.1", 13000);

// Send
stream.Write(data, 0, data.Length);

// Receive
int bytes = stream.Read(buffer, 0, buffer.Length);

// Async
await client.ConnectAsync(server, port);
await stream.WriteAsync(data, 0, data.Length);
await stream.ReadAsync(buffer, 0, buffer.Length);

// Properties
client.Connected      // bool
client.Available      // int (bytes ready to read)
client.ReceiveBufferSize  // int
client.SendBufferSize     // int

// Cleanup
client.Close();       // or let 'using' handle it
```

---

**For complete working examples, see:**
- `TcpClientDemo/Program.cs` - Full client implementation
- `TcpServer/Program.cs` - Full server implementation
- `README.md` - Detailed documentation
- `DEMO.md` - Step-by-step demonstration guide
