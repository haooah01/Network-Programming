using NetLayersDemo.Server.Endpoints;
using Serilog;
using Serilog.Events;

// Configure Serilog
Log.Logger = new LoggerConfiguration()
    .MinimumLevel.Information()
    .MinimumLevel.Override("Microsoft.AspNetCore", LogEventLevel.Warning)
    .Enrich.FromLogContext()
    .Enrich.WithMachineName()
    .Enrich.WithThreadId()
    .WriteTo.Console()
    .CreateLogger();

try
{
    Log.Information("Starting NetLayersDemo.Server");

    var builder = WebApplication.CreateBuilder(args);

    // Add Serilog
    builder.Host.UseSerilog();

    // Add services
    builder.Services.AddEndpointsApiExplorer();
    builder.Services.AddSwaggerGen(c =>
    {
        c.SwaggerDoc("v1", new() 
        { 
            Title = "NetLayersDemo API", 
            Version = "v1",
            Description = "A comprehensive .NET network programming demonstration API"
        });
    });

    // Add CORS
    builder.Services.AddCors(options =>
    {
        options.AddDefaultPolicy(policy =>
        {
            policy.AllowAnyOrigin()
                  .AllowAnyMethod()
                  .AllowAnyHeader();
        });
    });

    // Add health checks
    builder.Services.AddHealthChecks();

    var app = builder.Build();

    // Configure the HTTP request pipeline
    if (app.Environment.IsDevelopment())
    {
        app.UseSwagger();
        app.UseSwaggerUI(c =>
        {
            c.SwaggerEndpoint("/swagger/v1/swagger.json", "NetLayersDemo API v1");
            c.RoutePrefix = string.Empty; // Serve Swagger UI at root
        });
    }

    app.UseCors();
    app.UseSerilogRequestLogging();

    // Map endpoints
    app.MapEchoEndpoints();
    app.MapUriEndpoints();

    // Health check endpoint
    app.MapHealthChecks("/health");

    // Version endpoint
    app.MapGet("/version", () => new
    {
        Version = "1.0.0",
        Runtime = Environment.Version.ToString(),
        MachineName = Environment.MachineName,
        ProcessId = Environment.ProcessId,
        Timestamp = DateTime.UtcNow
    })
    .WithName("GetVersion")
    .WithTags("System")
    .WithOpenApi();

    // Root endpoint
    app.MapGet("/", () => new
    {
        Message = "Welcome to NetLayersDemo API",
        Documentation = "/swagger",
        Health = "/health",
        Version = "/version",
        Endpoints = new
        {
            Echo = "/api/echo",
            UriInspect = "/api/uri/inspect",
            UriCanonicalize = "/api/uri/canonicalize",
            UriValidate = "/api/uri/validate"
        }
    })
    .WithName("GetRoot")
    .WithTags("System")
    .WithOpenApi();

    await app.RunAsync();
}
catch (Exception ex)
{
    Log.Fatal(ex, "Application terminated unexpectedly");
}
finally
{
    Log.CloseAndFlush();
}
