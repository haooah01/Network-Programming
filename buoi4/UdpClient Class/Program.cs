using System;
using System.Net;
using System.Net.Sockets;
using System.Text;

namespace UdpClientClassDemo;

class Program
{
    static void Main(string[] args)
    {
        Console.WriteLine("UDP Client Demo");
        Console.WriteLine("Choose mode: 1=Send, 2=Receive");
        var mode = Console.ReadLine();
        if (mode == "1")
        {
            Console.Write("Target IP: ");
            var ip = Console.ReadLine() ?? "127.0.0.1";
            Console.Write("Target Port: ");
            var port = int.TryParse(Console.ReadLine(), out var p) ? p : 11000;
            Console.Write("Message: ");
            var msg = Console.ReadLine() ?? "Hello UDP!";
            SendUdp(ip, port, msg);
        }
        else if (mode == "2")
        {
            Console.Write("Listen Port: ");
            var port = int.TryParse(Console.ReadLine(), out var p) ? p : 11000;
            ReceiveUdp(port);
        }
        else
        {
            Console.WriteLine("Invalid mode.");
        }
    }

    static void SendUdp(string ip, int port, string message)
    {
        using var client = new UdpClient();
        var bytes = Encoding.UTF8.GetBytes(message);
        client.Send(bytes, bytes.Length, ip, port);
        Console.WriteLine($"Sent '{message}' to {ip}:{port}");
    }

    static void ReceiveUdp(int port)
    {
        using var client = new UdpClient(port);
        var ep = new IPEndPoint(IPAddress.Any, port);
        Console.WriteLine($"Listening on UDP port {port}...");
        while (true)
        {
            var data = client.Receive(ref ep);
            var msg = Encoding.UTF8.GetString(data);
            Console.WriteLine($"Received from {ep}: {msg}");
        }
    }
}
