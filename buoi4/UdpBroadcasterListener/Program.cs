using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading.Channels;

namespace UdpBroadcasterListener;

public class Program
{
    public static async Task Main(string[] args)
    {
        var builder = Host.CreateDefaultBuilder(args)
            .ConfigureAppConfiguration((hostingContext, config) =>
            {
                config.AddJsonFile("appsettings.json", optional: true);
                config.AddEnvironmentVariables(prefix: "UDPAPP_");
                config.AddCommandLine(args);
            })
            // Serilog removed for now; use default logging
            .ConfigureServices((context, services) =>
            {
                services.AddHostedService<UdpService>();
            });

        await builder.RunConsoleAsync();
    }
}

public class UdpService : BackgroundService
{
    private readonly IConfiguration _config;
    private readonly Microsoft.Extensions.Logging.ILogger<UdpService> _logger;
    private UdpClient? _udpClient;
    private IPEndPoint? _listenEndpoint;
    private string _mode;
    private string _txTarget;
    private int _txPort;
    private int _listenPort;
    private int _parallelism;
    private Channel<string>? _txChannel;

    public UdpService(IConfiguration config, ILogger<UdpService> logger)
    {
    _config = config;
    _logger = logger;
        _mode = config["mode"] ?? "listener";
        _txTarget = config["tx:target"] ?? "255.255.255.255";
        _txPort = int.TryParse(config["tx:port"], out var p) ? p : 11000;
        _listenPort = int.TryParse(config["listen:port"], out var lp) ? lp : 11000;
        _parallelism = int.TryParse(config["rx:parallelism"], out var par) ? par : 4;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        if (_mode == "listener")
        {
            await RunListener(stoppingToken);
        }
        else if (_mode == "broadcaster")
        {
            await RunBroadcaster(stoppingToken);
        }
        // Extend for multicast, metrics, health, etc.
    }

    private async Task RunListener(CancellationToken stoppingToken)
    {
        _listenEndpoint = new IPEndPoint(IPAddress.Any, _listenPort);
        _udpClient = new UdpClient(_listenPort);
    _logger.LogInformation("UDP Listener started on {Port}", _listenPort);
        while (!stoppingToken.IsCancellationRequested)
        {
            var result = await _udpClient.ReceiveAsync();
            var msg = Encoding.UTF8.GetString(result.Buffer);
            _logger.LogInformation("Received from {Source}: {Message}", result.RemoteEndPoint, msg);
        }
    }

    private async Task RunBroadcaster(CancellationToken stoppingToken)
    {
        _udpClient = new UdpClient();
        _udpClient.EnableBroadcast = true;
        var endpoint = new IPEndPoint(IPAddress.Parse(_txTarget), _txPort);
    _logger.LogInformation("UDP Broadcaster sending to {Target}:{Port}", _txTarget, _txPort);
        string payload = _config["payload"] ?? "Hello from broadcaster";
        while (!stoppingToken.IsCancellationRequested)
        {
            var bytes = Encoding.UTF8.GetBytes(payload);
            await _udpClient.SendAsync(bytes, bytes.Length, endpoint);
            _logger.LogInformation("Sent: {Payload}", payload);
            await Task.Delay(1000, stoppingToken); // 1 msg/sec
        }
    }
}
