namespace NetLayersDemo.Shared.Models;

/// <summary>
/// Represents the result of an echo operation
/// </summary>
public record EchoResult
{
    /// <summary>
    /// The echoed message
    /// </summary>
    public required string Message { get; init; }

    /// <summary>
    /// Timestamp when the echo was processed
    /// </summary>
    public DateTime Timestamp { get; init; } = DateTime.UtcNow;

    /// <summary>
    /// The source that processed the echo
    /// </summary>
    public required string Source { get; init; }

    /// <summary>
    /// Length of the original message
    /// </summary>
    public int MessageLength { get; init; }

    /// <summary>
    /// Additional metadata about the echo operation
    /// </summary>
    public Dictionary<string, object> Metadata { get; init; } = new();
}