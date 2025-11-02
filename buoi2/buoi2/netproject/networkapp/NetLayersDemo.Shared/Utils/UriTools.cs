using System.Text;
using NetLayersDemo.Shared.Models;

namespace NetLayersDemo.Shared.Utils;

/// <summary>
/// Utility class for URI operations and validation
/// </summary>
public static class UriTools
{
    /// <summary>
    /// Tries to parse a URI string
    /// </summary>
    /// <param name="uriString">The URI string to parse</param>
    /// <param name="uri">The parsed URI if successful</param>
    /// <returns>True if parsing succeeded, false otherwise</returns>
    public static bool TryParseUri(string uriString, out Uri? uri)
    {
        uri = null;
        
        if (string.IsNullOrWhiteSpace(uriString))
            return false;

        try
        {
            uri = new Uri(uriString, UriKind.RelativeOrAbsolute);
            return true;
        }
        catch (UriFormatException)
        {
            return false;
        }
    }

    /// <summary>
    /// Gets URI components from a URI
    /// </summary>
    /// <param name="uri">The URI to analyze</param>
    /// <returns>URI components</returns>
    public static UriInfo GetUriComponents(Uri uri)
    {
        ArgumentNullException.ThrowIfNull(uri);

        return new UriInfo
        {
            Scheme = uri.IsAbsoluteUri ? uri.Scheme : string.Empty,
            Host = uri.IsAbsoluteUri ? uri.Host : string.Empty,
            Port = uri.IsAbsoluteUri ? uri.Port : -1,
            Path = uri.IsAbsoluteUri ? uri.AbsolutePath : uri.OriginalString,
            Query = uri.IsAbsoluteUri ? uri.Query : string.Empty,
            Fragment = uri.IsAbsoluteUri ? uri.Fragment : string.Empty,
            Authority = uri.IsAbsoluteUri ? uri.Authority : string.Empty,
            UserInfo = uri.IsAbsoluteUri ? uri.UserInfo : string.Empty,
            IsAbsolute = uri.IsAbsoluteUri,
            IsWellFormed = Uri.IsWellFormedUriString(uri.OriginalString, UriKind.RelativeOrAbsolute)
        };
    }

    /// <summary>
    /// Canonicalizes a path by resolving relative components
    /// </summary>
    /// <param name="path">The path to canonicalize</param>
    /// <returns>The canonicalized path</returns>
    public static string CanonicalizePath(string path)
    {
        if (string.IsNullOrWhiteSpace(path))
            return "/";

        // Split path into segments
        var segments = path.Split('/', StringSplitOptions.RemoveEmptyEntries);
        var canonicalSegments = new List<string>();

        foreach (var segment in segments)
        {
            switch (segment)
            {
                case ".":
                    // Current directory - skip
                    break;
                case "..":
                    // Parent directory - remove last segment if exists
                    if (canonicalSegments.Count > 0)
                        canonicalSegments.RemoveAt(canonicalSegments.Count - 1);
                    break;
                default:
                    canonicalSegments.Add(segment);
                    break;
            }
        }

        var result = "/" + string.Join("/", canonicalSegments);
        
        // Preserve trailing slash if original had one
        if (path.EndsWith("/") && !result.EndsWith("/") && result.Length > 1)
            result += "/";

        return result;
    }

    /// <summary>
    /// Parses a URI string and returns detailed information about its components
    /// </summary>
    /// <param name="uriString">The URI string to parse</param>
    /// <returns>Detailed URI component information</returns>
    public static ParsedUriParts ParseUri(string uriString)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(uriString);

        var validationMessages = new List<string>();
        
        try
        {
            var uri = new Uri(uriString, UriKind.RelativeOrAbsolute);
            
            return new ParsedUriParts
            {
                OriginalUri = uriString,
                Scheme = uri.IsAbsoluteUri ? uri.Scheme : string.Empty,
                Host = uri.IsAbsoluteUri ? uri.Host : string.Empty,
                Port = uri.IsAbsoluteUri && !uri.IsDefaultPort ? uri.Port : null,
                PathAndQuery = uri.IsAbsoluteUri ? uri.PathAndQuery : uri.OriginalString,
                Fragment = uri.IsAbsoluteUri ? uri.Fragment : null,
                Authority = uri.IsAbsoluteUri ? uri.Authority : string.Empty,
                IsWellFormed = Uri.IsWellFormedUriString(uriString, UriKind.RelativeOrAbsolute),
                IsAbsolute = uri.IsAbsoluteUri,
                ValidationMessages = validationMessages
            };
        }
        catch (UriFormatException ex)
        {
            validationMessages.Add($"Invalid URI format: {ex.Message}");
            
            return new ParsedUriParts
            {
                OriginalUri = uriString,
                Scheme = string.Empty,
                Host = string.Empty,
                Port = null,
                PathAndQuery = string.Empty,
                Fragment = null,
                Authority = string.Empty,
                IsWellFormed = false,
                IsAbsolute = false,
                ValidationMessages = validationMessages
            };
        }
    }

    /// <summary>
    /// Validates a URI according to RFC 3986 standards
    /// </summary>
    /// <param name="uriString">The URI string to validate</param>
    /// <returns>True if the URI is valid, false otherwise</returns>
    public static bool IsValidUri(string uriString)
    {
        if (string.IsNullOrWhiteSpace(uriString))
            return false;

        return Uri.IsWellFormedUriString(uriString, UriKind.RelativeOrAbsolute);
    }

    /// <summary>
    /// Canonicalizes a URI by normalizing its components
    /// </summary>
    /// <param name="uriString">The URI string to canonicalize</param>
    /// <returns>The canonicalized URI string</returns>
    public static string CanonicalizeUri(string uriString)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(uriString);

        try
        {
            var uri = new Uri(uriString, UriKind.RelativeOrAbsolute);
            
            if (!uri.IsAbsoluteUri)
                return uriString;

            // Use UriBuilder to normalize the URI
            var builder = new UriBuilder(uri)
            {
                // Normalize scheme to lowercase
                Scheme = uri.Scheme.ToLowerInvariant(),
                // Normalize host to lowercase
                Host = uri.Host.ToLowerInvariant()
            };

            // Remove default ports
            if ((builder.Scheme == "http" && builder.Port == 80) ||
                (builder.Scheme == "https" && builder.Port == 443))
            {
                builder.Port = -1;
            }

            return builder.Uri.ToString();
        }
        catch (UriFormatException)
        {
            return uriString; // Return original if cannot canonicalize
        }
    }

    /// <summary>
    /// Extracts query parameters from a URI
    /// </summary>
    /// <param name="uri">The URI to extract parameters from</param>
    /// <returns>Dictionary of query parameters</returns>
    public static Dictionary<string, string> ExtractQueryParameters(Uri uri)
    {
        ArgumentNullException.ThrowIfNull(uri);

        var parameters = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);

        if (string.IsNullOrEmpty(uri.Query))
            return parameters;

        var query = uri.Query.TrimStart('?');
        var pairs = query.Split('&', StringSplitOptions.RemoveEmptyEntries);

        foreach (var pair in pairs)
        {
            var keyValue = pair.Split('=', 2);
            var key = Uri.UnescapeDataString(keyValue[0]);
            var value = keyValue.Length > 1 ? Uri.UnescapeDataString(keyValue[1]) : string.Empty;
            
            parameters[key] = value;
        }

        return parameters;
    }

    /// <summary>
    /// Builds a URI with query parameters
    /// </summary>
    /// <param name="baseUri">The base URI</param>
    /// <param name="parameters">Query parameters to add</param>
    /// <returns>URI with added query parameters</returns>
    public static Uri BuildUriWithQuery(string baseUri, Dictionary<string, string> parameters)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(baseUri);
        ArgumentNullException.ThrowIfNull(parameters);

        var builder = new UriBuilder(baseUri);
        
        if (parameters.Count == 0)
            return builder.Uri;

        var query = new StringBuilder();
        var first = true;

        foreach (var (key, value) in parameters)
        {
            if (!first) query.Append('&');
            query.Append(Uri.EscapeDataString(key));
            query.Append('=');
            query.Append(Uri.EscapeDataString(value));
            first = false;
        }

        builder.Query = query.ToString();
        return builder.Uri;
    }
}