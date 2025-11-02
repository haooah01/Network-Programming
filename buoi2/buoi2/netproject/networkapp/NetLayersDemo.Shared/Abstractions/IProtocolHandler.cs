namespace NetLayersDemo.Shared.Abstractions;

/// <summary>
/// Defines a contract for protocol handlers that can process URIs with specific schemes
/// </summary>
public interface IProtocolHandler
{
    /// <summary>
    /// Determines if this handler can process the given URI
    /// </summary>
    /// <param name="uri">The URI to check</param>
    /// <returns>True if this handler can process the URI, false otherwise</returns>
    bool CanHandle(Uri uri);

    /// <summary>
    /// Executes the protocol-specific logic for the given URI
    /// </summary>
    /// <param name="uri">The URI to process</param>
    /// <param name="cancellationToken">Cancellation token for the operation</param>
    /// <returns>The result of processing the URI</returns>
    Task<string> ExecuteAsync(Uri uri, CancellationToken cancellationToken = default);

    /// <summary>
    /// Gets the name of the protocol this handler supports
    /// </summary>
    string ProtocolName { get; }
}