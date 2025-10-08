using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using System.Collections.Generic;

class Program
{
    static void Main(string[] args)
    {
        // Bind to an ephemeral port (0) and let OS pick a free port
        var listener = new TcpListener(IPAddress.Loopback, 0);
        listener.Start();
        var boundPort = ((IPEndPoint)listener.LocalEndpoint).Port;
        Console.WriteLine($"[Server] Listening on 127.0.0.1:{boundPort} (CTRL+C to stop)");

        // In-memory, thread-safe log store
        var logs = new List<string>();
        var logsLock = new object();
        void AddLog(string s)
        {
            lock (logsLock)
            {
                logs.Add($"[{DateTime.Now:HH:mm:ss}] {s}");
                if (logs.Count > 200) logs.RemoveAt(0);
            }
            Console.WriteLine(s);
        }

        // Try to start a simple HTTP UI on a small range of ports
        int uiPort = -1;
        System.Net.HttpListener? http = null;
        for (int tryPort = 5000; tryPort < 5010; tryPort++)
        {
            try
            {
                http = new System.Net.HttpListener();
                http.Prefixes.Add($"http://localhost:{tryPort}/");
                http.Start();
                uiPort = tryPort;
                break;
            }
            catch (HttpListenerException)
            {
                http = null;
            }
        }

        if (uiPort != -1 && http != null)
        {
            AddLog($"HTTP UI listening on http://localhost:{uiPort}/");
            // Serve UI and /logs
            Task.Run(() =>
            {
                while (http.IsListening)
                {
                    try
                    {
                        var ctx = http.GetContext();
                        var req = ctx.Request;
                        var resp = ctx.Response;
                        if (req?.Url != null && req.Url.AbsolutePath == "/logs")
                        {
                            string json;
                            lock (logsLock)
                            {
                                json = System.Text.Json.JsonSerializer.Serialize(logs);
                            }
                            var bytes = Encoding.UTF8.GetBytes(json);
                            resp.ContentType = "application/json";
                            resp.OutputStream.Write(bytes, 0, bytes.Length);
                            resp.Close();
                        }
                        else
                        {
                            // Serve a static index.html from ../ui/index.html if present
                            var uiPath = Path.GetFullPath(Path.Combine(Directory.GetCurrentDirectory(), "..", "ui", "index.html"));
                            if (File.Exists(uiPath))
                            {
                                var html = File.ReadAllText(uiPath);
                                var bytes = Encoding.UTF8.GetBytes(html);
                                resp.ContentType = "text/html";
                                resp.OutputStream.Write(bytes, 0, bytes.Length);
                                resp.Close();
                            }
                            else
                            {
                                var msg = "UI not available";
                                var bytes = Encoding.UTF8.GetBytes(msg);
                                resp.OutputStream.Write(bytes, 0, bytes.Length);
                                resp.Close();
                            }
                        }
                    }
                    catch (Exception ex)
                    {
                        // swallow and continue
                        AddLog("HTTP UI error: " + ex.Message);
                    }
                }
            });
        }

        // Print a JSON line with ports so external runner can pick them up
        var portsObj = new { port = boundPort, ui = uiPort };
        Console.WriteLine(System.Text.Json.JsonSerializer.Serialize(portsObj));

        try
        {
            while (true)
            {
                using var client = listener.AcceptTcpClient();
                var remote = client.Client.RemoteEndPoint;
                Console.WriteLine($"[Server] Accepted connection from {remote}");

                using var stream = client.GetStream();
                var buffer = new byte[4096];
                var bytesRead = stream.Read(buffer, 0, buffer.Length);
                if (bytesRead > 0)
                {
                    var received = Encoding.UTF8.GetString(buffer, 0, bytesRead);
                    Console.WriteLine($"[Server] Received: {received}");

                    var reply = $"Hello from server (received {bytesRead} bytes)";
                    var outBytes = Encoding.UTF8.GetBytes(reply);
                    stream.Write(outBytes, 0, outBytes.Length);
                    Console.WriteLine("[Server] Reply sent, closing connection\n");
                }
            }
        }
        catch (SocketException se)
        {
            Console.WriteLine("[Server] SocketException: " + se.Message);
        }
        finally
        {
            listener.Stop();
        }
    }
}