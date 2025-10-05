using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using System.Text.Json;
using NetLayersDemo.Shared.Abstractions;
using NetLayersDemo.Shared.Protocols;
using NetLayersDemo.Shared.Utils;

// Configure services
var builder = Host.CreateApplicationBuilder(args);

// Add logging
builder.Logging.ClearProviders()
    .AddConsole()
    .SetMinimumLevel(LogLevel.Information);

// Add HttpClient
builder.Services.AddHttpClient("NetLayersDemo", client =>
{
    client.BaseAddress = new Uri("http://localhost:5050/");
    client.DefaultRequestHeaders.Add("User-Agent", "NetLayersDemo.Client/1.0");
});

// Register protocol handlers
builder.Services.AddTransient<IProtocolHandler, HttpProtocolHandler>();
builder.Services.AddTransient<IProtocolHandler, FileProtocolHandler>();
builder.Services.AddTransient<IProtocolHandler, CustomSchemeHandler>();

// Build the host
var host = builder.Build();

var logger = host.Services.GetRequiredService<ILogger<Program>>();
var httpClientFactory = host.Services.GetRequiredService<IHttpClientFactory>();
var protocolHandlers = host.Services.GetServices<IProtocolHandler>();

logger.LogInformation("NetLayersDemo Client starting...");

// Create HTTP client
var httpClient = httpClientFactory.CreateClient("NetLayersDemo");

try
{
    await RunDemoAsync(httpClient, protocolHandlers, logger);
}
catch (Exception ex)
{
    logger.LogError(ex, "An error occurred during demo execution");
}

logger.LogInformation("NetLayersDemo Client finished.");

static async Task RunDemoAsync(HttpClient httpClient, IEnumerable<IProtocolHandler> protocolHandlers, ILogger logger)
{
    Console.WriteLine("=== NetLayersDemo Client ===");
    Console.WriteLine();

    // Test API endpoints
    await TestApiEndpointsAsync(httpClient, logger);
    
    // Test protocol handlers
    await TestProtocolHandlersAsync(protocolHandlers, logger);
    
    // Test URI utilities
    TestUriUtilities(logger);
    
    Console.WriteLine();
    Console.WriteLine("Demo completed. Press any key to exit...");
    Console.ReadKey();
}

static async Task TestApiEndpointsAsync(HttpClient httpClient, ILogger logger)
{
    Console.WriteLine("=== Testing API Endpoints ===");
    
    try
    {
        // Test root endpoint
        logger.LogInformation("Testing root endpoint...");
        var rootResponse = await httpClient.GetStringAsync("/");
        var rootData = JsonSerializer.Deserialize<JsonElement>(rootResponse);
        Console.WriteLine($"✓ Root: {rootData.GetProperty("Message").GetString()}");
        
        // Test version endpoint
        logger.LogInformation("Testing version endpoint...");
        var versionResponse = await httpClient.GetStringAsync("/version");
        var versionData = JsonSerializer.Deserialize<JsonElement>(versionResponse);
        Console.WriteLine($"✓ Version: {versionData.GetProperty("Version").GetString()}");
        
        // Test health endpoint
        logger.LogInformation("Testing health endpoint...");
        var healthResponse = await httpClient.GetStringAsync("/health");
        Console.WriteLine($"✓ Health: {healthResponse}");
        
        // Test echo endpoint
        logger.LogInformation("Testing echo endpoint...");
        var echoResponse = await httpClient.GetStringAsync("/api/echo?message=Hello from Client!");
        var echoData = JsonSerializer.Deserialize<JsonElement>(echoResponse);
        Console.WriteLine($"✓ Echo: {echoData.GetProperty("originalMessage").GetString()}");
        
        // Test URI inspection
        logger.LogInformation("Testing URI inspection...");
        var uriResponse = await httpClient.GetStringAsync("/api/uri/inspect?uri=https://example.com:8080/path?query=value");
        var uriData = JsonSerializer.Deserialize<JsonElement>(uriResponse);
        Console.WriteLine($"✓ URI Inspect: Scheme={uriData.GetProperty("scheme").GetString()}, Host={uriData.GetProperty("host").GetString()}");
    }
    catch (Exception ex)
    {
        logger.LogError(ex, "Error testing API endpoints");
        Console.WriteLine($"✗ API Test failed: {ex.Message}");
    }
    
    Console.WriteLine();
}

static async Task TestProtocolHandlersAsync(IEnumerable<IProtocolHandler> protocolHandlers, ILogger logger)
{
    Console.WriteLine("=== Testing Protocol Handlers ===");
    
    var testUris = new[]
    {
        "https://www.example.com",
        "file:///C:/temp/test.txt",
        "custom://action/data"
    };
    
    foreach (var uriString in testUris)
    {
        try
        {
            var uri = new Uri(uriString);
            var handler = protocolHandlers.FirstOrDefault(h => h.CanHandle(uri));
            
            if (handler != null)
            {
                logger.LogInformation("Testing protocol handler for {Uri}", uriString);
                var result = await handler.ExecuteAsync(uri);
                Console.WriteLine($"✓ {uriString}: {result}");
            }
            else
            {
                Console.WriteLine($"✗ {uriString}: No handler found");
            }
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "Error testing protocol handler for {Uri}", uriString);
            Console.WriteLine($"✗ {uriString}: {ex.Message}");
        }
    }
    
    Console.WriteLine();
}

static void TestUriUtilities(ILogger logger)
{
    Console.WriteLine("=== Testing URI Utilities ===");
    
    try
    {
        // Test URI parsing
        var testUri = "https://user:pass@example.com:8080/path/to/resource?query=value&param=123#fragment";
        logger.LogInformation("Testing URI parsing for {Uri}", testUri);
        
        if (UriTools.TryParseUri(testUri, out var parsedUri))
        {
            var components = UriTools.GetUriComponents(parsedUri);
            Console.WriteLine($"✓ URI Parsed successfully:");
            Console.WriteLine($"  - Scheme: {components.Scheme}");
            Console.WriteLine($"  - Host: {components.Host}");
            Console.WriteLine($"  - Port: {components.Port}");
            Console.WriteLine($"  - Path: {components.Path}");
            Console.WriteLine($"  - Query: {components.Query}");
            Console.WriteLine($"  - Fragment: {components.Fragment}");
        }
        else
        {
            Console.WriteLine($"✗ Failed to parse URI: {testUri}");
        }
        
        // Test URI validation
        var validationTests = new[]
        {
            ("https://example.com", true),
            ("invalid-uri", false),
            ("ftp://files.example.com/file.txt", true),
            ("not a uri at all", false)
        };
        
        Console.WriteLine();
        Console.WriteLine("URI Validation Tests:");
        
        foreach (var (uri, expectedValid) in validationTests)
        {
            var isValid = UriTools.IsValidUri(uri);
            var result = isValid == expectedValid ? "✓" : "✗";
            Console.WriteLine($"  {result} {uri}: {(isValid ? "Valid" : "Invalid")}");
        }
    }
    catch (Exception ex)
    {
        logger.LogError(ex, "Error testing URI utilities");
        Console.WriteLine($"✗ URI Utilities test failed: {ex.Message}");
    }
    
    Console.WriteLine();
}
