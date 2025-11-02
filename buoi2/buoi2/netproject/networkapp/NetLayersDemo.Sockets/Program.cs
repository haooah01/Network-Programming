using System.Net;
using System.Net.Sockets;
using System.Text;

Console.WriteLine("=== NetLayersDemo TCP Echo Server/Client ===");
Console.WriteLine();
Console.WriteLine("Choose mode:");
Console.WriteLine("1. Server");
Console.WriteLine("2. Client");
Console.WriteLine("3. Both (Server + Client)");
Console.Write("Enter choice (1-3): ");

var choice = Console.ReadLine();
var cts = new CancellationTokenSource();

// Handle Ctrl+C gracefully
Console.CancelKeyPress += (sender, e) =>
{
    e.Cancel = true;
    cts.Cancel();
    Console.WriteLine("\nShutdown requested...");
};

try
{
    switch (choice)
    {
        case "1":
            await RunServerAsync(cts.Token);
            break;
        case "2":
            await RunClientAsync(cts.Token);
            break;
        case "3":
            await RunBothAsync(cts.Token);
            break;
        default:
            Console.WriteLine("Invalid choice. Exiting...");
            break;
    }
}
catch (OperationCanceledException)
{
    Console.WriteLine("Operation was cancelled.");
}
catch (Exception ex)
{
    Console.WriteLine($"Error: {ex.Message}");
}

Console.WriteLine("Press any key to exit...");
Console.ReadKey();

static async Task RunServerAsync(CancellationToken cancellationToken)
{
    const int port = 8080;
    var listener = new TcpListener(IPAddress.Any, port);
    
    try
    {
        listener.Start();
        Console.WriteLine($"TCP Echo Server listening on port {port}");
        Console.WriteLine("Waiting for clients... (Press Ctrl+C to stop)");
        
        while (!cancellationToken.IsCancellationRequested)
        {
            try
            {
                // Accept client with cancellation support
                var tcpClient = await AcceptTcpClientAsync(listener, cancellationToken);
                
                // Handle client in background
                _ = Task.Run(() => HandleClientAsync(tcpClient, cancellationToken), cancellationToken);
            }
            catch (OperationCanceledException)
            {
                break;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error accepting client: {ex.Message}");
            }
        }
    }
    finally
    {
        listener.Stop();
        Console.WriteLine("Server stopped.");
    }
}

static async Task<TcpClient> AcceptTcpClientAsync(TcpListener listener, CancellationToken cancellationToken)
{
    while (!cancellationToken.IsCancellationRequested)
    {
        if (listener.Pending())
        {
            return await listener.AcceptTcpClientAsync();
        }
        await Task.Delay(100, cancellationToken);
    }
    throw new OperationCanceledException();
}

static async Task HandleClientAsync(TcpClient client, CancellationToken cancellationToken)
{
    var clientEndpoint = client.Client.RemoteEndPoint;
    Console.WriteLine($"Client connected: {clientEndpoint}");
    
    try
    {
        using (client)
        using (var stream = client.GetStream())
        {
            var buffer = new byte[4096];
            
            while (!cancellationToken.IsCancellationRequested && client.Connected)
            {
                try
                {
                    var bytesRead = await stream.ReadAsync(buffer, 0, buffer.Length, cancellationToken);
                    
                    if (bytesRead == 0)
                    {
                        Console.WriteLine($"Client {clientEndpoint} disconnected.");
                        break;
                    }
                    
                    var message = Encoding.UTF8.GetString(buffer, 0, bytesRead);
                    Console.WriteLine($"Received from {clientEndpoint}: {message.Trim()}");
                    
                    // Echo the message back
                    var echoMessage = $"Echo: {message}";
                    var echoBytes = Encoding.UTF8.GetBytes(echoMessage);
                    await stream.WriteAsync(echoBytes, 0, echoBytes.Length, cancellationToken);
                    await stream.FlushAsync(cancellationToken);
                    
                    Console.WriteLine($"Echoed to {clientEndpoint}: {echoMessage.Trim()}");
                }
                catch (OperationCanceledException)
                {
                    break;
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error handling client {clientEndpoint}: {ex.Message}");
                    break;
                }
            }
        }
    }
    catch (Exception ex)
    {
        Console.WriteLine($"Error with client {clientEndpoint}: {ex.Message}");
    }
    finally
    {
        Console.WriteLine($"Client {clientEndpoint} session ended.");
    }
}

static async Task RunClientAsync(CancellationToken cancellationToken)
{
    const string serverHost = "localhost";
    const int serverPort = 8080;
    
    try
    {
        using var client = new TcpClient();
        
        Console.WriteLine($"Connecting to {serverHost}:{serverPort}...");
        await client.ConnectAsync(serverHost, serverPort);
        Console.WriteLine("Connected to server!");
        
        using var stream = client.GetStream();
        
        // Start receiving task
        var receiveTask = Task.Run(async () =>
        {
            var buffer = new byte[4096];
            try
            {
                while (!cancellationToken.IsCancellationRequested && client.Connected)
                {
                    var bytesRead = await stream.ReadAsync(buffer, 0, buffer.Length, cancellationToken);
                    if (bytesRead == 0) break;
                    
                    var response = Encoding.UTF8.GetString(buffer, 0, bytesRead);
                    Console.WriteLine($"Server: {response.Trim()}");
                }
            }
            catch (OperationCanceledException) { }
            catch (Exception ex)
            {
                Console.WriteLine($"Receive error: {ex.Message}");
            }
        }, cancellationToken);
        
        // Send messages
        Console.WriteLine("Enter messages to send (type 'quit' to exit):");
        
        while (!cancellationToken.IsCancellationRequested)
        {
            Console.Write("Client: ");
            var input = Console.ReadLine();
            
            if (string.IsNullOrEmpty(input) || input.ToLower() == "quit")
                break;
            
            try
            {
                var messageBytes = Encoding.UTF8.GetBytes(input + "\n");
                await stream.WriteAsync(messageBytes, 0, messageBytes.Length, cancellationToken);
                await stream.FlushAsync(cancellationToken);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Send error: {ex.Message}");
                break;
            }
        }
        
        await receiveTask;
    }
    catch (Exception ex)
    {
        Console.WriteLine($"Client error: {ex.Message}");
    }
    
    Console.WriteLine("Client disconnected.");
}

static async Task RunBothAsync(CancellationToken cancellationToken)
{
    Console.WriteLine("Starting both server and client...");
    
    // Start server in background
    var serverTask = Task.Run(() => RunServerAsync(cancellationToken), cancellationToken);
    
    // Wait a moment for server to start
    await Task.Delay(1000, cancellationToken);
    
    // Start client
    var clientTask = Task.Run(() => RunClientAsync(cancellationToken), cancellationToken);
    
    // Wait for either to complete
    await Task.WhenAny(serverTask, clientTask);
}
