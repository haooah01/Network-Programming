using System.Buffers;
using System.Diagnostics;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

Console.OutputEncoding = Encoding.UTF8;

var options = TcpSenderOptions.Parse(args);
if (options.ShowHelp)
{
    TcpSenderOptions.PrintHelp();
    return;
}

var sender = new TcpMessageSender(options, Console.Out, Console.Error);
var result = await sender.ExecuteAsync();

if (result.IsSuccess)
{
    Console.WriteLine($"Response: {result.Response}");
    Console.WriteLine($"Elapsed: {result.Elapsed.TotalMilliseconds:F1} ms");
    Environment.ExitCode = 0;
}
else
{
    Environment.ExitCode = 1;
}

public sealed record SenderResult(bool IsSuccess, string Response, TimeSpan Elapsed);

public sealed class TcpMessageSender
{
    private readonly TcpSenderOptions _options;
    private readonly TextWriter _stdout;
    private readonly TextWriter _stderr;

    public TcpMessageSender(TcpSenderOptions options, TextWriter stdout, TextWriter stderr)
    {
        _options = options;
        _stdout = stdout;
        _stderr = stderr;
    }

    public async Task<SenderResult> ExecuteAsync(CancellationToken cancellationToken = default)
    {
        using var client = new TcpClient();

        try
        {
            client.ReceiveTimeout = (int)_options.Timeout.TotalMilliseconds;
            client.SendTimeout = (int)_options.Timeout.TotalMilliseconds;

            var stopwatch = Stopwatch.StartNew();

            await client.ConnectAsync(_options.Host, _options.Port, cancellationToken);

            await using var stream = client.GetStream();
            stream.ReadTimeout = (int)_options.Timeout.TotalMilliseconds;
            stream.WriteTimeout = (int)_options.Timeout.TotalMilliseconds;

            var payload = BuildPayload();
            await stream.WriteAsync(payload, cancellationToken);
            await stream.FlushAsync(cancellationToken);

            if (_options.FullDuplex) // leave connection open for more data
            {
                _stdout.WriteLine("Message sent (full-duplex mode, not waiting for response).");
                return new SenderResult(true, string.Empty, stopwatch.Elapsed);
            }

            client.Client.Shutdown(SocketShutdown.Send);

            var response = await ReadResponseAsync(stream, cancellationToken);

            stopwatch.Stop();
            return new SenderResult(true, response, stopwatch.Elapsed);
        }
        catch (Exception ex) when (ex is SocketException or IOException or OperationCanceledException)
        {
            _stderr.WriteLine($"Error: {ex.Message}");
            return new SenderResult(false, string.Empty, TimeSpan.Zero);
        }
    }

    private byte[] BuildPayload()
    {
        var builder = new StringBuilder(_options.Message);
        if (_options.AppendNewLine && !builder.ToString().EndsWith("\n", StringComparison.Ordinal))
        {
            builder.Append('\n');
        }

        return _options.Encoding.GetBytes(builder.ToString());
    }

    private async Task<string> ReadResponseAsync(NetworkStream stream, CancellationToken cancellationToken)
    {
        var buffer = ArrayPool<byte>.Shared.Rent(1024);
        try
        {
            using var ms = new MemoryStream();

            while (true)
            {
                var bytesRead = await stream.ReadAsync(buffer, cancellationToken);
                if (bytesRead <= 0)
                {
                    break;
                }

                ms.Write(buffer, 0, bytesRead);

                if (!stream.DataAvailable)
                {
                    break;
                }
            }

            return _options.Encoding.GetString(ms.ToArray());
        }
        finally
        {
            ArrayPool<byte>.Shared.Return(buffer);
        }
    }
}

public sealed class TcpSenderOptions
{
    public string Host { get; private set; } = IPAddress.Loopback.ToString();
    public int Port { get; private set; } = 13000;
    public string Message { get; private set; } = "Hello from TcpSender";
    public Encoding Encoding { get; private set; } = Encoding.ASCII;
    public bool AppendNewLine { get; private set; } = true;
    public bool FullDuplex { get; private set; }
    public TimeSpan Timeout { get; private set; } = TimeSpan.FromSeconds(5);
    public bool ShowHelp { get; private set; }

    public static TcpSenderOptions Parse(string[] args)
    {
        var options = new TcpSenderOptions();

        for (var i = 0; i < args.Length; i++)
        {
            switch (args[i])
            {
                case "--host":
                case "-H":
                    options.Host = ParseHost(args, ref i);
                    break;
                case "--port":
                case "-p":
                    options.Port = ParsePort(args, ref i);
                    break;
                case "--message":
                case "-m":
                    options.Message = ParseMessage(args, ref i);
                    break;
                case "--encoding":
                    options.Encoding = ParseEncoding(args, ref i);
                    break;
                case "--no-newline":
                    options.AppendNewLine = false;
                    break;
                case "--timeout":
                    options.Timeout = ParseTimeout(args, ref i);
                    break;
                case "--full-duplex":
                    options.FullDuplex = true;
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

    private static string ParseHost(string[] args, ref int index)
    {
        EnsureHasValue(args, index);
        return args[++index];
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

    private static string ParseMessage(string[] args, ref int index)
    {
        EnsureHasValue(args, index);
        return args[++index];
    }

    private static Encoding ParseEncoding(string[] args, ref int index)
    {
        EnsureHasValue(args, index);
        var value = args[++index];
        return value.ToLowerInvariant() switch
        {
            "utf8" => Encoding.UTF8,
            "utf-8" => Encoding.UTF8,
            "ascii" => Encoding.ASCII,
            "unicode" => Encoding.Unicode,
            _ => throw new ArgumentException($"Unsupported encoding '{value}'. Try utf8, ascii, or unicode."),
        };
    }

    private static TimeSpan ParseTimeout(string[] args, ref int index)
    {
        EnsureHasValue(args, index);
        if (!int.TryParse(args[++index], out var seconds) || seconds <= 0)
        {
            throw new ArgumentException("Timeout must be a positive integer number of seconds.");
        }

        return TimeSpan.FromSeconds(seconds);
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
        Console.WriteLine("Simple TCP sender\n");
        Console.WriteLine("Usage:");
        Console.WriteLine("  dotnet run --project TcpSenderApp -- [options]\n");
        Console.WriteLine("Options:");
        Console.WriteLine("  -H, --host <name>         Hostname or IP address (default: 127.0.0.1)");
        Console.WriteLine("  -p, --port <number>       Port number (default: 13000)");
        Console.WriteLine("  -m, --message <text>      Message to send (default: 'Hello from TcpSender')");
        Console.WriteLine("      --encoding <name>     Encoding (ascii, utf8, unicode; default: ascii)");
        Console.WriteLine("      --no-newline          Do not append a trailing newline to the message");
        Console.WriteLine("      --timeout <seconds>   Connection/read timeout (default: 5)");
        Console.WriteLine("      --full-duplex         Send message without waiting for response");
        Console.WriteLine("  -h, --help                Show this help message\n");
    }
}
