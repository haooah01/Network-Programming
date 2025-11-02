using NetLayersDemo.Shared.Utils;
using System.Web;

namespace NetLayersDemo.Server.Endpoints;

/// <summary>
/// URI inspection endpoints for the API
/// </summary>
public static class UriEndpoints
{
    /// <summary>
    /// Maps URI-related endpoints
    /// </summary>
    /// <param name="app">The web application builder</param>
    public static void MapUriEndpoints(this WebApplication app)
    {
        var uriGroup = app.MapGroup("/api/uri")
            .WithTags("URI")
            .WithOpenApi();

        uriGroup.MapGet("/inspect", InspectUri)
            .WithName("InspectUri")
            .WithSummary("Inspect and parse a URI")
            .WithDescription("Parses the provided URI and returns detailed component information");

        uriGroup.MapGet("/canonicalize", CanonicalizeUri)
            .WithName("CanonicalizeUri")
            .WithSummary("Canonicalize a URI")
            .WithDescription("Normalizes the provided URI according to RFC 3986");

        uriGroup.MapGet("/validate", ValidateUri)
            .WithName("ValidateUri")
            .WithSummary("Validate a URI")
            .WithDescription("Validates if the provided URI is well-formed");
    }

    /// <summary>
    /// GET /api/uri/inspect?u=https://example.com/path?query=value#fragment
    /// </summary>
    private static IResult InspectUri(string? u, ILogger<Program> logger)
    {
        logger.LogInformation("Processing URI inspection request");

        if (string.IsNullOrEmpty(u))
        {
            return Results.BadRequest(new { error = "URI parameter 'u' is required" });
        }

        try
        {
            // URL decode the parameter
            var decodedUri = HttpUtility.UrlDecode(u);
            logger.LogInformation("Inspecting URI: {Uri}", decodedUri);

            var parsedUri = UriTools.ParseUri(decodedUri);
            
            logger.LogInformation("Successfully parsed URI");
            return Results.Ok(parsedUri);
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "Error parsing URI: {Uri}", u);
            return Results.BadRequest(new { error = $"Error parsing URI: {ex.Message}" });
        }
    }

    /// <summary>
    /// GET /api/uri/canonicalize?u=https://EXAMPLE.COM:443/Path/../path?query=value
    /// </summary>
    private static IResult CanonicalizeUri(string? u, ILogger<Program> logger)
    {
        logger.LogInformation("Processing URI canonicalization request");

        if (string.IsNullOrEmpty(u))
        {
            return Results.BadRequest(new { error = "URI parameter 'u' is required" });
        }

        try
        {
            var decodedUri = HttpUtility.UrlDecode(u);
            logger.LogInformation("Canonicalizing URI: {Uri}", decodedUri);

            var canonicalUri = UriTools.CanonicalizeUri(decodedUri);
            
            var result = new
            {
                OriginalUri = decodedUri,
                CanonicalUri = canonicalUri,
                Timestamp = DateTime.UtcNow
            };

            logger.LogInformation("Successfully canonicalized URI");
            return Results.Ok(result);
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "Error canonicalizing URI: {Uri}", u);
            return Results.BadRequest(new { error = $"Error canonicalizing URI: {ex.Message}" });
        }
    }

    /// <summary>
    /// GET /api/uri/validate?u=https://example.com/path
    /// </summary>
    private static IResult ValidateUri(string? u, ILogger<Program> logger)
    {
        logger.LogInformation("Processing URI validation request");

        if (string.IsNullOrEmpty(u))
        {
            return Results.BadRequest(new { error = "URI parameter 'u' is required" });
        }

        try
        {
            var decodedUri = HttpUtility.UrlDecode(u);
            logger.LogInformation("Validating URI: {Uri}", decodedUri);

            var isValid = UriTools.IsValidUri(decodedUri);
            
            var result = new
            {
                Uri = decodedUri,
                IsValid = isValid,
                IsWellFormed = Uri.IsWellFormedUriString(decodedUri, UriKind.RelativeOrAbsolute),
                Timestamp = DateTime.UtcNow
            };

            logger.LogInformation("URI validation result: {IsValid}", isValid);
            return Results.Ok(result);
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "Error validating URI: {Uri}", u);
            return Results.BadRequest(new { error = $"Error validating URI: {ex.Message}" });
        }
    }
}