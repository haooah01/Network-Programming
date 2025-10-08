using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading.Tasks;
using Xunit;

public class TcpIntegrationTests
{
    [Fact]
    public async Task ClientServerExchange_HappyPath()
    {
        var listener = new TcpListener(IPAddress.Loopback, 0);
        listener.Start();
        var port = ((IPEndPoint)listener.LocalEndpoint).Port;

        var serverTask = Task.Run(async () =>
        {
            using var client = await listener.AcceptTcpClientAsync();
            using var stream = client.GetStream();
            var buffer = new byte[1024];
            var read = await stream.ReadAsync(buffer, 0, buffer.Length);
            var rec = Encoding.UTF8.GetString(buffer, 0, read);

            var reply = "pong";
            var outb = Encoding.UTF8.GetBytes(reply);
            await stream.WriteAsync(outb, 0, outb.Length);
        });

        var clientTask = Task.Run(async () =>
        {
            using var c = new TcpClient();
            await c.ConnectAsync("127.0.0.1", port);
            using var s = c.GetStream();
            var msg = "ping";
            var outb = Encoding.UTF8.GetBytes(msg);
            await s.WriteAsync(outb, 0, outb.Length);

            var buffer = new byte[1024];
            var read = await s.ReadAsync(buffer, 0, buffer.Length);
            var resp = Encoding.UTF8.GetString(buffer, 0, read);
            return resp;
        });

        var clientResp = await clientTask;
        await serverTask; // ensure server finished

        Assert.Equal("pong", clientResp);
    }
}
