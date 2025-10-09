using System;
using System.IO;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using Xunit;

namespace TcpListenerApp.Tests;

public class ServerTests
{
    [Fact]
    public async Task EchoServer_UppercasesPayload()
    {
        var options = TcpListenerOptions.Parse(new[] { "--port", "0" });
        var server = new TcpEchoServer(options);
        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(5));

        var serverTask = server.RunAsync(cts.Token);

        await WaitForServerAsync(server, cts.Token);

        using var client = new TcpClient();
        await client.ConnectAsync(server.BoundEndpoint!.Address, server.BoundEndpoint.Port);

        using var stream = client.GetStream();
        var payload = Encoding.ASCII.GetBytes("hello world");
        await stream.WriteAsync(payload);

        var buffer = new byte[1024];
        var bytesRead = await stream.ReadAsync(buffer, cts.Token);

        var response = Encoding.ASCII.GetString(buffer, 0, bytesRead);
        Assert.Equal("HELLO WORLD", response);

        client.Close();
        cts.Cancel();

        await serverTask;
    }

    [Fact]
    public async Task SenderReceivesUppercaseResponse()
    {
        var serverOptions = TcpListenerOptions.Parse(new[] { "--port", "0" });
        var server = new TcpEchoServer(serverOptions);
        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(5));

        var serverTask = server.RunAsync(cts.Token);
        await WaitForServerAsync(server, cts.Token);

        var senderArgs = new[]
        {
            "--host", server.BoundEndpoint!.Address.ToString(),
            "--port", server.BoundEndpoint.Port.ToString(),
            "--message", "integration"
        };

        var senderOptions = TcpSenderOptions.Parse(senderArgs);
        using var stdout = new StringWriter();
        using var stderr = new StringWriter();

        var sender = new TcpMessageSender(senderOptions, stdout, stderr);
        var result = await sender.ExecuteAsync(cts.Token);

        Assert.True(result.IsSuccess, stderr.ToString());
        Assert.StartsWith("INTEGRATION", result.Response);

        cts.Cancel();
        await serverTask;
    }

    private static async Task WaitForServerAsync(TcpEchoServer server, CancellationToken cancellationToken)
    {
        while (!cancellationToken.IsCancellationRequested)
        {
            if (server.BoundEndpoint is not null)
            {
                return;
            }

            await Task.Delay(50, cancellationToken);
        }

        throw new TimeoutException("Server failed to start before cancellation was requested.");
    }
}
