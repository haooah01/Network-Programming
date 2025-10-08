using System;
using System.Net.Sockets;
using System.Text;

namespace TcpClientDemo
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("=== TCP Client Demo ===");
            Console.WriteLine("Based on Microsoft TcpClient Class Documentation\n");

            bool running = true;
            while (running)
            {
                Console.WriteLine("\nChoose an option:");
                Console.WriteLine("1. Simple Connect and Send");
                Console.WriteLine("2. Multiple Messages");
                Console.WriteLine("3. Check Connection Properties");
                Console.WriteLine("4. Async Connect Demo");
                Console.WriteLine("5. Exit");
                Console.Write("\nYour choice: ");

                string choice = Console.ReadLine();

                switch (choice)
                {
                    case "1":
                        SimpleConnect();
                        break;
                    case "2":
                        MultipleMessages();
                        break;
                    case "3":
                        CheckConnectionProperties();
                        break;
                    case "4":
                        AsyncConnectDemo().Wait();
                        break;
                    case "5":
                        running = false;
                        break;
                    default:
                        Console.WriteLine("Invalid choice!");
                        break;
                }
            }

            Console.WriteLine("\nGoodbye!");
        }

        /// <summary>
        /// Example from Microsoft Documentation
        /// Simple connection, send message, and receive response
        /// </summary>
        static void SimpleConnect()
        {
            string server = "127.0.0.1";
            Console.Write("Enter message to send: ");
            string message = Console.ReadLine() ?? "Hello Server!";

            Connect(server, message);
        }

        /// <summary>
        /// Microsoft Documentation Example: Connect method
        /// </summary>
        static void Connect(String server, String message)
        {
            try
            {
                // Create a TcpClient.
                // Note, for this client to work you need to have a TcpServer
                // connected to the same address as specified by the server, port
                // combination.
                Int32 port = 13000;

                // Prefer a using declaration to ensure the instance is Disposed later.
                using TcpClient client = new TcpClient(server, port);

                // Translate the passed message into ASCII and store it as a Byte array.
                Byte[] data = System.Text.Encoding.ASCII.GetBytes(message);

                // Get a client stream for reading and writing.
                NetworkStream stream = client.GetStream();

                // Send the message to the connected TcpServer.
                stream.Write(data, 0, data.Length);

                Console.WriteLine("Sent: {0}", message);

                // Receive the server response.

                // Buffer to store the response bytes.
                data = new Byte[256];

                // String to store the response ASCII representation.
                String responseData = String.Empty;

                // Read the first batch of the TcpServer response bytes.
                Int32 bytes = stream.Read(data, 0, data.Length);
                responseData = System.Text.Encoding.ASCII.GetString(data, 0, bytes);
                Console.WriteLine("Received: {0}", responseData);

                // Explicit close is not necessary since TcpClient.Dispose() will be
                // called automatically.
                // stream.Close();
                // client.Close();
            }
            catch (ArgumentNullException e)
            {
                Console.WriteLine("ArgumentNullException: {0}", e);
            }
            catch (SocketException e)
            {
                Console.WriteLine("SocketException: {0}", e);
            }

            Console.WriteLine("\nPress Enter to continue...");
            Console.Read();
        }

        /// <summary>
        /// Send multiple messages to demonstrate persistent connection
        /// </summary>
        static void MultipleMessages()
        {
            string server = "127.0.0.1";
            Int32 port = 13000;

            try
            {
                using TcpClient client = new TcpClient(server, port);
                NetworkStream stream = client.GetStream();

                Console.WriteLine($"Connected to {server}:{port}");
                Console.WriteLine("Enter messages (type 'quit' to exit):\n");

                while (true)
                {
                    Console.Write("> ");
                    string message = Console.ReadLine();

                    if (message?.ToLower() == "quit")
                        break;

                    // Send message
                    Byte[] data = Encoding.ASCII.GetBytes(message);
                    stream.Write(data, 0, data.Length);

                    // Receive response
                    data = new Byte[256];
                    Int32 bytes = stream.Read(data, 0, data.Length);
                    string response = Encoding.ASCII.GetString(data, 0, bytes);
                    Console.WriteLine($"Server: {response}\n");
                }
            }
            catch (Exception e)
            {
                Console.WriteLine($"Exception: {e.Message}");
            }
        }

        /// <summary>
        /// Demonstrate TcpClient properties
        /// </summary>
        static void CheckConnectionProperties()
        {
            string server = "127.0.0.1";
            Int32 port = 13000;

            try
            {
                using TcpClient client = new TcpClient();
                
                Console.WriteLine("\n=== TcpClient Properties ===");
                Console.WriteLine($"Connected: {client.Connected}");
                Console.WriteLine($"ExclusiveAddressUse: {client.ExclusiveAddressUse}");
                
                // Connect to server
                Console.WriteLine($"\nConnecting to {server}:{port}...");
                client.Connect(server, port);
                
                Console.WriteLine($"Connected: {client.Connected}");
                Console.WriteLine($"Available bytes: {client.Available}");
                Console.WriteLine($"ReceiveBufferSize: {client.ReceiveBufferSize} bytes");
                Console.WriteLine($"SendBufferSize: {client.SendBufferSize} bytes");
                Console.WriteLine($"ReceiveTimeout: {client.ReceiveTimeout} ms");
                Console.WriteLine($"SendTimeout: {client.SendTimeout} ms");
                Console.WriteLine($"NoDelay (Nagle's algorithm disabled): {client.NoDelay}");
                
                // Get underlying Socket info
                if (client.Client != null)
                {
                    Console.WriteLine($"\nUnderlying Socket:");
                    Console.WriteLine($"  LocalEndPoint: {client.Client.LocalEndPoint}");
                    Console.WriteLine($"  RemoteEndPoint: {client.Client.RemoteEndPoint}");
                    Console.WriteLine($"  AddressFamily: {client.Client.AddressFamily}");
                    Console.WriteLine($"  SocketType: {client.Client.SocketType}");
                    Console.WriteLine($"  ProtocolType: {client.Client.ProtocolType}");
                }

                // Send a test message
                NetworkStream stream = client.GetStream();
                Byte[] data = Encoding.ASCII.GetBytes("Property Test");
                stream.Write(data, 0, data.Length);
                
                // Read response
                data = new Byte[256];
                Int32 bytes = stream.Read(data, 0, data.Length);
                string response = Encoding.ASCII.GetString(data, 0, bytes);
                Console.WriteLine($"\nTest message response: {response}");
            }
            catch (Exception e)
            {
                Console.WriteLine($"Exception: {e.Message}");
            }

            Console.WriteLine("\nPress Enter to continue...");
            Console.Read();
        }

        /// <summary>
        /// Demonstrate async connection using ConnectAsync
        /// </summary>
        static async System.Threading.Tasks.Task AsyncConnectDemo()
        {
            string server = "127.0.0.1";
            Int32 port = 13000;

            try
            {
                using TcpClient client = new TcpClient();
                
                Console.WriteLine($"\nAsync connecting to {server}:{port}...");
                
                // Use ConnectAsync for non-blocking connection
                await client.ConnectAsync(server, port);
                
                Console.WriteLine("Connected asynchronously!");

                NetworkStream stream = client.GetStream();
                string message = "Async Hello!";
                
                Byte[] data = Encoding.ASCII.GetBytes(message);
                await stream.WriteAsync(data, 0, data.Length);
                Console.WriteLine($"Sent: {message}");

                data = new Byte[256];
                Int32 bytes = await stream.ReadAsync(data, 0, data.Length);
                string response = Encoding.ASCII.GetString(data, 0, bytes);
                Console.WriteLine($"Received: {response}");
            }
            catch (Exception e)
            {
                Console.WriteLine($"Exception: {e.Message}");
            }

            Console.WriteLine("\nPress Enter to continue...");
            Console.Read();
        }
    }
}
