using System;
using System.Net.Sockets;
using System.Text;

class Program
{
    static void Main(string[] args)
    {
        string server = "127.0.0.1";
        int port = 8080;
        if (args.Length > 0) server = args[0];
        if (args.Length > 1 && int.TryParse(args[1], out var p)) port = p;

        try
        {
            using var client = new TcpClient();
            Console.WriteLine($"[Client] Connecting to {server}:{port}...");
            client.Connect(server, port);
            Console.WriteLine("[Client] Connected");

            using var stream = client.GetStream();
            var msg = "Hello from client";
            var outBytes = Encoding.UTF8.GetBytes(msg);
            stream.Write(outBytes, 0, outBytes.Length);
            Console.WriteLine($"[Client] Sent: {msg}");

            var buffer = new byte[4096];
            var bytesRead = stream.Read(buffer, 0, buffer.Length);
            if (bytesRead > 0)
            {
                var resp = Encoding.UTF8.GetString(buffer, 0, bytesRead);
                Console.WriteLine($"[Client] Received: {resp}");
            }

            Console.WriteLine("[Client] Closing");
        }
        catch (Exception ex)
        {
            Console.WriteLine("[Client] Error: " + ex.Message);
        }
    }
}