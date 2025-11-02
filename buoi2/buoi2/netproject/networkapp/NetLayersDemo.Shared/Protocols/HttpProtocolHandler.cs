using NetLayersDemo.Shared.Abstractions;

namespace NetLayersDemo.Shared.Protocols;

/// <summary>
/// Protocol handler for HTTP and HTTPS schemes
/// </summary>
public class HttpProtocolHandler : IProtocolHandler
{
    private readonly HttpClient _httpClient;

    public string ProtocolName => "HTTP/HTTPS";

    public HttpProtocolHandler(HttpClient httpClient)
    {
        _httpClient = httpClient ?? throw new ArgumentNullException(nameof(httpClient));
    }

    public bool CanHandle(Uri uri)
    {
        ArgumentNullException.ThrowIfNull(uri);
        return uri.Scheme.Equals("http", StringComparison.OrdinalIgnoreCase) ||
               uri.Scheme.Equals("https", StringComparison.OrdinalIgnoreCase);
    }

    public async Task<string> ExecuteAsync(Uri uri, CancellationToken cancellationToken = default)
    {
        ArgumentNullException.ThrowIfNull(uri);

        if (!CanHandle(uri))
            throw new NotSupportedException($"URI scheme '{uri.Scheme}' is not supported by this handler");

        try
        {
            using var response = await _httpClient.GetAsync(uri, cancellationToken);
            
            var content = await response.Content.ReadAsStringAsync(cancellationToken);
            
            var result = new
            {
                StatusCode = (int)response.StatusCode,
                StatusDescription = response.ReasonPhrase,
                ContentLength = content.Length,
                ContentType = response.Content.Headers.ContentType?.ToString(),
                Headers = response.Headers.ToDictionary(h => h.Key, h => string.Join(", ", h.Value)),
                ContentPreview = content.Length > 200 ? content[..200] + "..." : content
            };

            return System.Text.Json.JsonSerializer.Serialize(result, new System.Text.Json.JsonSerializerOptions 
            { 
                WriteIndented = true 
            });
        }
        catch (HttpRequestException ex)
        {
            return $"HTTP request failed: {ex.Message}";
        }
        catch (TaskCanceledException ex) when (ex.InnerException is TimeoutException)
        {
            return "HTTP request timed out";
        }
        catch (Exception ex)
        {
            return $"Unexpected error: {ex.Message}";
        }
    }
}