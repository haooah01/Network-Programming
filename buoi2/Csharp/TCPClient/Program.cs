using System;
using System.IO;
using System.Net.Sockets;
using System.Text;
using System.Threading;

namespace TCPClient
{
    class TCPChatClient
    {
        private TcpClient client;
        private NetworkStream stream;
        private bool isConnected;
        private Thread receiveThread;

        public bool Connect(string serverIP, int port)
        {
            try
            {
                client = new TcpClient();
                client.Connect(serverIP, port);
                stream = client.GetStream();
                isConnected = true;

                Console.WriteLine($"Connected to server {serverIP}:{port}");
                
                // Start receiving messages in background
                receiveThread = new Thread(ReceiveMessages);
                receiveThread.Start();
                
                return true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Connection failed: {ex.Message}");
                return false;
            }
        }

        private void ReceiveMessages()
        {
            byte[] buffer = new byte[1024];
            
            try
            {
                while (isConnected && client.Connected)
                {
                    int bytesRead = stream.Read(buffer, 0, buffer.Length);
                    if (bytesRead == 0)
                    {
                        Console.WriteLine("Server disconnected");
                        break;
                    }

                    string message = Encoding.UTF8.GetString(buffer, 0, bytesRead);
                    Console.WriteLine(message);
                }
            }
            catch (Exception ex)
            {
                if (isConnected)
                {
                    Console.WriteLine($"Error receiving message: {ex.Message}");
                }
            }
            finally
            {
                isConnected = false;
            }
        }

        public void SendMessage(string message)
        {
            if (!isConnected || !client.Connected)
            {
                Console.WriteLine("Not connected to server");
                return;
            }

            try
            {
                byte[] data = Encoding.UTF8.GetBytes(message);
                stream.Write(data, 0, data.Length);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error sending message: {ex.Message}");
                isConnected = false;
            }
        }

        public void Disconnect()
        {
            isConnected = false;
            stream?.Close();
            client?.Close();
            receiveThread?.Join(1000); // Wait up to 1 second for thread to finish
            Console.WriteLine("Disconnected from server");
        }

        public bool IsConnected => isConnected && client?.Connected == true;
    }

    class Program
    {
        static void Main(string[] args)
        {
            TCPChatClient chatClient = new TCPChatClient();
            
            Console.WriteLine("=== TCP Chat Client ===");
            Console.WriteLine("Commands:");
            Console.WriteLine("  /connect <ip> <port> - Connect to server");
            Console.WriteLine("  /disconnect - Disconnect from server");
            Console.WriteLine("  /quit - Exit application");
            Console.WriteLine("  <message> - Send message to chat");
            Console.WriteLine("========================");

            bool running = true;
            while (running)
            {
                Console.Write("> ");
                string input = Console.ReadLine();
                
                if (string.IsNullOrWhiteSpace(input))
                    continue;

                if (input.StartsWith("/"))
                {
                    string[] parts = input.Split(' ', StringSplitOptions.RemoveEmptyEntries);
                    string command = parts[0].ToLower();

                    switch (command)
                    {
                        case "/connect":
                            if (parts.Length >= 3)
                            {
                                string ip = parts[1];
                                if (int.TryParse(parts[2], out int port))
                                {
                                    if (chatClient.IsConnected)
                                    {
                                        Console.WriteLine("Already connected. Disconnect first.");
                                    }
                                    else
                                    {
                                        chatClient.Connect(ip, port);
                                    }
                                }
                                else
                                {
                                    Console.WriteLine("Invalid port number");
                                }
                            }
                            else
                            {
                                Console.WriteLine("Usage: /connect <ip> <port>");
                                Console.WriteLine("Example: /connect 127.0.0.1 8888");
                            }
                            break;

                        case "/disconnect":
                            if (chatClient.IsConnected)
                            {
                                chatClient.Disconnect();
                            }
                            else
                            {
                                Console.WriteLine("Not connected to any server");
                            }
                            break;

                        case "/quit":
                            if (chatClient.IsConnected)
                            {
                                chatClient.Disconnect();
                            }
                            running = false;
                            break;

                        default:
                            Console.WriteLine("Unknown command. Available commands: /connect, /disconnect, /quit");
                            break;
                    }
                }
                else
                {
                    // Send message
                    if (chatClient.IsConnected)
                    {
                        chatClient.SendMessage(input);
                    }
                    else
                    {
                        Console.WriteLine("Not connected to server. Use /connect <ip> <port> to connect.");
                    }
                }
            }

            Console.WriteLine("Client shutting down...");
        }
    }
}
