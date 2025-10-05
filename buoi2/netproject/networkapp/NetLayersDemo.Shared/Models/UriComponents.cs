namespace NetLayersDemo.Shared.Models;

/// <summary>
/// Represents the components of a URI
/// </summary>
public class UriInfo
{
    /// <summary>
    /// The scheme component (e.g., "http", "https", "ftp")
    /// </summary>
    public string Scheme { get; set; } = string.Empty;

    /// <summary>
    /// The host component (e.g., "example.com")
    /// </summary>
    public string Host { get; set; } = string.Empty;

    /// <summary>
    /// The port number (-1 for default port)
    /// </summary>
    public int Port { get; set; } = -1;

    /// <summary>
    /// The path component (e.g., "/path/to/resource")
    /// </summary>
    public string Path { get; set; } = string.Empty;

    /// <summary>
    /// The query component (e.g., "?key=value")
    /// </summary>
    public string Query { get; set; } = string.Empty;

    /// <summary>
    /// The fragment component (e.g., "#section")
    /// </summary>
    public string Fragment { get; set; } = string.Empty;

    /// <summary>
    /// The authority component (e.g., "user:pass@host:port")
    /// </summary>
    public string Authority { get; set; } = string.Empty;

    /// <summary>
    /// User information component (e.g., "user:pass")
    /// </summary>
    public string UserInfo { get; set; } = string.Empty;

    /// <summary>
    /// Whether this URI is absolute
    /// </summary>
    public bool IsAbsolute { get; set; }

    /// <summary>
    /// Whether this URI is well-formed
    /// </summary>
    public bool IsWellFormed { get; set; }
}