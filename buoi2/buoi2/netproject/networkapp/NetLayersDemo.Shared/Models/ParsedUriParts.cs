namespace NetLayersDemo.Shared.Models;

/// <summary>
/// Represents the parsed components of a URI
/// </summary>
public record ParsedUriParts
{
    /// <summary>
    /// The original URI string
    /// </summary>
    public required string OriginalUri { get; init; }

    /// <summary>
    /// The scheme (protocol) of the URI
    /// </summary>
    public required string Scheme { get; init; }

    /// <summary>
    /// The host component of the URI
    /// </summary>
    public required string Host { get; init; }

    /// <summary>
    /// The port number, if specified
    /// </summary>
    public int? Port { get; init; }

    /// <summary>
    /// The path and query string combined
    /// </summary>
    public required string PathAndQuery { get; init; }

    /// <summary>
    /// The fragment (anchor) part of the URI
    /// </summary>
    public string? Fragment { get; init; }

    /// <summary>
    /// The authority component (userinfo, host, port)
    /// </summary>
    public required string Authority { get; init; }

    /// <summary>
    /// Whether the URI is considered well-formed
    /// </summary>
    public bool IsWellFormed { get; init; }

    /// <summary>
    /// Whether the URI is absolute
    /// </summary>
    public bool IsAbsolute { get; init; }

    /// <summary>
    /// Additional validation messages, if any
    /// </summary>
    public List<string> ValidationMessages { get; init; } = new();
}