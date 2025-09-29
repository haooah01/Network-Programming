using System;
using System.Net.Http;
using System.Threading.Tasks;

namespace MiniNet
{
    class MiniNetDemo
    {
        static async Task Main(string[] args)
        {
            Console.WriteLine("=== Mini Networking Demo ===");
            Console.WriteLine("Fetching content from example.com...\n");

            try
            {
                using var http = new HttpClient();
                string html = await http.GetStringAsync("https://example.com");
                
                // Display first 200 characters to avoid overwhelming output
                int maxLength = Math.Min(html.Length, 200);
                Console.WriteLine($"HTML Content (first {maxLength} characters):");
                Console.WriteLine(html[..maxLength]);
                Console.WriteLine("...");
                
                Console.WriteLine($"\nTotal content length: {html.Length} characters");
                Console.WriteLine("Successfully fetched content from web server!");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error: {ex.Message}");
            }

            Console.WriteLine("\nPress ENTER to exit...");
            Console.ReadLine();
        }
    }
}
