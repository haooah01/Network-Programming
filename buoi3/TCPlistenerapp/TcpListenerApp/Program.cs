using System.Net;
using System.Net.Sockets;
using System.Text;

Console.OutputEncoding = Encoding.UTF8;

var options = TcpListenerOptions.Parse(args);
if (options.ShowHelp)
{
    TcpListenerOptions.PrintHelp();
    return;
}

var cancellationSource = new CancellationTokenSource();
Console.CancelKeyPress += (_, eventArgs) =>
{
    Console.WriteLine("\nCancellation requested. Shutting down...");
    eventArgs.Cancel = true;
    cancellationSource.Cancel();
};

var server = new TcpEchoServer(options);
await server.RunAsync(cancellationSource.Token);

internal sealed class TcpEchoServer
{
    private readonly TcpListenerOptions _options;
    private TcpListener? _listener;

    public IPEndPoint? BoundEndpoint => (IPEndPoint?)_listener?.LocalEndpoint;

    public TcpEchoServer(TcpListenerOptions options)
    {
        _options = options;
    }

    public async Task RunAsync(CancellationToken cancellationToken)
    {
        _listener = new TcpListener(_options.IPAddress, _options.Port);

        try
        {
            _listener.Start(_options.Backlog);
            Console.WriteLine($"Listening on {_listener.LocalEndpoint}; press Ctrl+C to stop.");

            var tasks = new List<Task>();

            while (!cancellationToken.IsCancellationRequested)
            {
                if (!_listener.Pending())
                {
                    await Task.Delay(200, cancellationToken);
                    continue;
                }

                var client = await _listener.AcceptTcpClientAsync(cancellationToken);
                tasks.Add(HandleClientAsync(client, cancellationToken));
            }

            await Task.WhenAll(tasks);
        }
        catch (OperationCanceledException)
        {
            // Expected during shutdown.
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine($"Server error: {ex.Message}");
        }
        finally
        {
            if (_listener is not null)
            {
                _listener.Stop();
                Console.WriteLine("Listener stopped.");
            }
        }
    }

    private static async Task HandleClientAsync(TcpClient client, CancellationToken cancellationToken)
    {
        using (client)
        {
            var remoteEndpoint = client.Client.RemoteEndPoint;
            Console.WriteLine($"Accepted connection from {remoteEndpoint}.");

            var buffer = new byte[1024];
            var stream = client.GetStream();

            try
            {
                while (!cancellationToken.IsCancellationRequested)
                {
                    var bytesRead = await stream.ReadAsync(buffer, cancellationToken);
                    if (bytesRead == 0)
                    {
                        Console.WriteLine($"Client {remoteEndpoint} disconnected.");
                        break;
                    }

                    var receivedText = Encoding.ASCII.GetString(buffer, 0, bytesRead);
                    Console.WriteLine($"Received ({remoteEndpoint}): {receivedText.TrimEnd()}");

                    var response = Encoding.ASCII.GetBytes(receivedText.ToUpperInvariant());
                    await stream.WriteAsync(response, cancellationToken);
                    Console.WriteLine($"Sent ({remoteEndpoint}): {Encoding.ASCII.GetString(response).TrimEnd()}");
                }
            }
            catch (OperationCanceledException)
            {
                Console.WriteLine($"Client handler cancelled for {remoteEndpoint}.");
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine($"Client {remoteEndpoint} error: {ex.Message}");
            }
        }
    }
}

sealed class TcpListenerOptions
{
    public IPAddress IPAddress { get; private set; } = IPAddress.Loopback;
    public int Port { get; private set; } = 13000;
    public int Backlog { get; private set; } = 100;
    public bool ShowHelp { get; private set; }

    public static TcpListenerOptions Parse(string[] args)
    {
        var options = new TcpListenerOptions();

        for (var i = 0; i < args.Length; i++)
        {
            switch (args[i])
            {
                case "--port":
                case "-p":
                    options.Port = ParsePort(args, ref i);
                    break;
                case "--ip":
                case "-i":
                    options.IPAddress = ParseIPAddress(args, ref i);
                    break;
                case "--backlog":
                case "-b":
                    options.Backlog = ParseBacklog(args, ref i);
                    break;
                case "--help":
                case "-h":
                case "-?":
                    options.ShowHelp = true;
                    break;
                default:
                    throw new ArgumentException($"Unknown argument '{args[i]}'. Use --help to see available options.");
            }
        }

        return options;
    }

    private static int ParsePort(string[] args, ref int index)
    {
        EnsureHasValue(args, index);
        if (!int.TryParse(args[++index], out var port) || port is < IPEndPoint.MinPort or > IPEndPoint.MaxPort)
        {
            throw new ArgumentException("Port must be an integer between 0 and 65535.");
        }

        return port;
    }

    private static IPAddress ParseIPAddress(string[] args, ref int index)
    {
        EnsureHasValue(args, index);

        var value = args[++index];
        if (!IPAddress.TryParse(value, out var address))
        {
            throw new ArgumentException($"Invalid IP address '{value}'.");
        }

        return address;
    }

    private static int ParseBacklog(string[] args, ref int index)
    {
        EnsureHasValue(args, index);

        if (!int.TryParse(args[++index], out var backlog) || backlog <= 0)
        {
            throw new ArgumentException("Backlog must be a positive integer.");
        }

        return backlog;
    }

    private static void EnsureHasValue(string[] args, int index)
    {
        if (index + 1 >= args.Length)
        {
            throw new ArgumentException($"Missing value for argument '{args[index]}'.");
        }
    }

    public static void PrintHelp()
    {
        Console.WriteLine("Simple TCP echo listener\n");
        Console.WriteLine("Usage:");
        Console.WriteLine("  dotnet run -- [options]\n");
        Console.WriteLine("Options:");
        Console.WriteLine("  -p, --port <number>       Port to listen on (default: 13000)");
        Console.WriteLine("  -i, --ip <address>        Local IP address to bind (default: 127.0.0.1)");
        Console.WriteLine("  -b, --backlog <number>    Maximum pending connection backlog (default: 100)");
        Console.WriteLine("  -h, --help                Show this help message\n");
    }
}
