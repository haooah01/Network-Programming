using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;

namespace TcpServer
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("=== TCP Server Demo ===");
            Console.WriteLine("Starting server on port 13000...\n");

            TcpListener server = null;
            try
            {
                // Set the TcpListener on port 13000
                Int32 port = 13000;
                IPAddress localAddr = IPAddress.Parse("127.0.0.1");

                // TcpListener server = new TcpListener(port);
                server = new TcpListener(localAddr, port);

                // Start listening for client requests
                server.Start();

                Console.WriteLine($"Server started on {localAddr}:{port}");
                Console.WriteLine("Waiting for connections...\n");

                // Buffer for reading data
                Byte[] bytes = new Byte[256];
                String data = null;

                int clientCount = 0;

                // Enter the listening loop
                while (true)
                {
                    Console.WriteLine("Waiting for a connection...");

                    // Perform a blocking call to accept requests
                    // You could also use server.AcceptSocket() here
                    TcpClient client = server.AcceptTcpClient();
                    clientCount++;
                    
                    Console.WriteLine($"Client #{clientCount} connected!");

                    data = null;

                    // Get a stream object for reading and writing
                    NetworkStream stream = client.GetStream();

                    int i;

                    // Loop to receive all the data sent by the client
                    while ((i = stream.Read(bytes, 0, bytes.Length)) != 0)
                    {
                        // Translate data bytes to an ASCII string
                        data = Encoding.ASCII.GetString(bytes, 0, i);
                        Console.WriteLine($"Received from client #{clientCount}: {data}");

                        // Process the data sent by the client
                        data = data.ToUpper();

                        byte[] msg = Encoding.ASCII.GetBytes($"Echo: {data}");

                        // Send back a response
                        stream.Write(msg, 0, msg.Length);
                        Console.WriteLine($"Sent to client #{clientCount}: Echo: {data}\n");
                    }

                    // Shutdown and end connection
                    Console.WriteLine($"Client #{clientCount} disconnected.\n");
                    client.Close();
                }
            }
            catch (SocketException e)
            {
                Console.WriteLine($"SocketException: {e}");
            }
            finally
            {
                // Stop listening for new clients
                server?.Stop();
                Console.WriteLine("\nServer stopped.");
            }

            Console.WriteLine("\nPress Enter to exit...");
            Console.Read();
        }
    }
}
