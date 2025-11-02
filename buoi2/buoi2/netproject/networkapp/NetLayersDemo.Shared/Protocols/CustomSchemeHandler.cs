using NetLayersDemo.Shared.Abstractions;

namespace NetLayersDemo.Shared.Protocols;

/// <summary>
/// Protocol handler for custom schemes (demo purposes)
/// </summary>
public class CustomSchemeHandler : IProtocolHandler
{
    private static readonly HashSet<string> SupportedSchemes = new(StringComparer.OrdinalIgnoreCase)
    {
        "custom", "demo", "test", "example"
    };

    public string ProtocolName => "Custom Schemes";

    public bool CanHandle(Uri uri)
    {
        ArgumentNullException.ThrowIfNull(uri);
        return SupportedSchemes.Contains(uri.Scheme);
    }

    public async Task<string> ExecuteAsync(Uri uri, CancellationToken cancellationToken = default)
    {
        ArgumentNullException.ThrowIfNull(uri);

        if (!CanHandle(uri))
            throw new NotSupportedException($"URI scheme '{uri.Scheme}' is not supported by this handler");

        // Simulate some async work
        await Task.Delay(100, cancellationToken);

        var result = new
        {
            Message = $"Handled custom scheme: {uri.Scheme}",
            Uri = uri.ToString(),
            Host = uri.Host,
            Path = uri.AbsolutePath,
            Query = uri.Query,
            Fragment = uri.Fragment,
            Timestamp = DateTime.UtcNow,
            Handler = nameof(CustomSchemeHandler),
            SupportedSchemes = SupportedSchemes.ToArray()
        };

        return System.Text.Json.JsonSerializer.Serialize(result, new System.Text.Json.JsonSerializerOptions 
        { 
            WriteIndented = true 
        });
    }
}