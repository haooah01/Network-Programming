using NetLayersDemo.Shared.Models;
using NetLayersDemo.Shared.Utils;

namespace NetLayersDemo.Server.Endpoints;

/// <summary>
/// Echo endpoints for the API
/// </summary>
public static class EchoEndpoints
{
    /// <summary>
    /// Maps echo-related endpoints
    /// </summary>
    /// <param name="app">The web application builder</param>
    public static void MapEchoEndpoints(this WebApplication app)
    {
        var echoGroup = app.MapGroup("/api/echo")
            .WithTags("Echo")
            .WithOpenApi();

        echoGroup.MapGet("/", GetEcho)
            .WithName("GetEcho")
            .WithSummary("Echo a message")
            .WithDescription("Returns the provided message with additional metadata");

        echoGroup.MapPost("/", PostEcho)
            .WithName("PostEcho")
            .WithSummary("Echo a message via POST")
            .WithDescription("Returns the provided message from request body with additional metadata");
    }

    /// <summary>
    /// GET /api/echo?msg=hello
    /// </summary>
    private static IResult GetEcho(string? msg, ILogger<Program> logger)
    {
        logger.LogInformation("Processing GET echo request with message: {Message}", msg);

        if (string.IsNullOrEmpty(msg))
        {
            return Results.BadRequest(new { error = "Message parameter 'msg' is required" });
        }

        if (msg.Length > 1000)
        {
            return Results.BadRequest(new { error = "Message too long. Maximum length is 1000 characters." });
        }

        var result = new EchoResult
        {
            Message = msg,
            Source = "NetLayersDemo.Server",
            MessageLength = msg.Length,
            Metadata = new Dictionary<string, object>
            {
                ["method"] = "GET",
                ["endpoint"] = "/api/echo",
                ["server"] = Environment.MachineName,
                ["processId"] = Environment.ProcessId,
                ["threadId"] = Thread.CurrentThread.ManagedThreadId
            }
        };

        logger.LogInformation("Successfully processed echo request");
        return Results.Ok(result);
    }

    /// <summary>
    /// POST /api/echo
    /// </summary>
    private static IResult PostEcho(EchoRequest request, ILogger<Program> logger)
    {
        logger.LogInformation("Processing POST echo request");

        if (request?.Message == null)
        {
            return Results.BadRequest(new { error = "Message is required in request body" });
        }

        if (request.Message.Length > 1000)
        {
            return Results.BadRequest(new { error = "Message too long. Maximum length is 1000 characters." });
        }

        var result = new EchoResult
        {
            Message = request.Message,
            Source = "NetLayersDemo.Server",
            MessageLength = request.Message.Length,
            Metadata = new Dictionary<string, object>
            {
                ["method"] = "POST",
                ["endpoint"] = "/api/echo",
                ["server"] = Environment.MachineName,
                ["processId"] = Environment.ProcessId,
                ["threadId"] = Thread.CurrentThread.ManagedThreadId,
                ["clientInfo"] = request.ClientInfo ?? "Unknown"
            }
        };

        logger.LogInformation("Successfully processed POST echo request");
        return Results.Ok(result);
    }
}

/// <summary>
/// Request model for POST echo endpoint
/// </summary>
public record EchoRequest
{
    /// <summary>
    /// The message to echo
    /// </summary>
    public required string Message { get; init; }

    /// <summary>
    /// Optional client information
    /// </summary>
    public string? ClientInfo { get; init; }
}