using System;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;

namespace TCPServer
{
    class TCPChatServer
    {
        private TcpListener server;
        private List<TcpClient> clients;
        private List<Thread> clientThreads;
        private bool isRunning;

        public TCPChatServer(string ipAddress, int port)
        {
            server = new TcpListener(IPAddress.Parse(ipAddress), port);
            clients = new List<TcpClient>();
            clientThreads = new List<Thread>();
            isRunning = false;
        }

        public void Start()
        {
            server.Start();
            isRunning = true;
            Console.WriteLine($"Server started on {((IPEndPoint)server.LocalEndpoint).Address}:{((IPEndPoint)server.LocalEndpoint).Port}");
            Console.WriteLine("Waiting for clients...");

            while (isRunning)
            {
                try
                {
                    TcpClient client = server.AcceptTcpClient();
                    clients.Add(client);
                    
                    Console.WriteLine($"Client connected: {((IPEndPoint)client.Client.RemoteEndPoint).Address}");
                    Console.WriteLine($"Total clients: {clients.Count}");

                    Thread clientThread = new Thread(() => HandleClient(client));
                    clientThreads.Add(clientThread);
                    clientThread.Start();
                }
                catch (Exception ex)
                {
                    if (isRunning)
                    {
                        Console.WriteLine($"Error accepting client: {ex.Message}");
                    }
                }
            }
        }

        private void HandleClient(TcpClient client)
        {
            NetworkStream stream = client.GetStream();
            byte[] buffer = new byte[1024];
            string clientEndpoint = ((IPEndPoint)client.Client.RemoteEndPoint).Address.ToString();

            try
            {
                while (client.Connected && isRunning)
                {
                    int bytesRead = stream.Read(buffer, 0, buffer.Length);
                    if (bytesRead == 0)
                    {
                        break; // Client disconnected
                    }

                    string message = Encoding.UTF8.GetString(buffer, 0, bytesRead);
                    Console.WriteLine($"[{clientEndpoint}]: {message}");

                    // Broadcast message to all other clients
                    BroadcastMessage($"[{clientEndpoint}]: {message}", client);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Client {clientEndpoint} error: {ex.Message}");
            }
            finally
            {
                Console.WriteLine($"Client {clientEndpoint} disconnected");
                clients.Remove(client);
                client.Close();
                Console.WriteLine($"Total clients: {clients.Count}");
            }
        }

        private void BroadcastMessage(string message, TcpClient sender)
        {
            byte[] data = Encoding.UTF8.GetBytes(message);
            List<TcpClient> disconnectedClients = new List<TcpClient>();

            foreach (TcpClient client in clients)
            {
                if (client != sender && client.Connected)
                {
                    try
                    {
                        NetworkStream stream = client.GetStream();
                        stream.Write(data, 0, data.Length);
                    }
                    catch (Exception)
                    {
                        disconnectedClients.Add(client);
                    }
                }
            }

            // Remove disconnected clients
            foreach (TcpClient client in disconnectedClients)
            {
                clients.Remove(client);
                client.Close();
            }
        }

        public void Stop()
        {
            isRunning = false;
            
            foreach (TcpClient client in clients)
            {
                client.Close();
            }
            clients.Clear();

            server?.Stop();
            Console.WriteLine("Server stopped");
        }
    }

    class Program
    {
        static void Main(string[] args)
        {
            TCPChatServer server = new TCPChatServer("127.0.0.1", 8888);
            
            Console.WriteLine("=== TCP Chat Server ===");
            Console.WriteLine("Press 'q' to quit server");
            Console.WriteLine("========================");

            // Start server in background thread
            Thread serverThread = new Thread(server.Start);
            serverThread.Start();

            // Handle user input
            while (true)
            {
                ConsoleKeyInfo keyInfo = Console.ReadKey(true);
                if (keyInfo.KeyChar == 'q' || keyInfo.KeyChar == 'Q')
                {
                    server.Stop();
                    break;
                }
            }

            Console.WriteLine("Server shutting down...");
        }
    }
}
