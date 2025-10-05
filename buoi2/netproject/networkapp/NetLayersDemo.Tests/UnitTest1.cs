using NetLayersDemo.Shared.Utils;
using NetLayersDemo.Shared.Protocols;
using NetLayersDemo.Shared.Models;

namespace NetLayersDemo.Tests;

public class UriToolsTests
{
    [Theory]
    [InlineData("https://example.com", true)]
    [InlineData("http://localhost:8080", true)]
    [InlineData("ftp://files.example.com", true)]
    [InlineData("invalid-uri", true)] // This is treated as relative URI
    [InlineData("not a uri", false)] // This has spaces which makes it invalid
    [InlineData("", false)]
    public void IsValidUri_ShouldReturnExpectedResult(string uri, bool expected)
    {
        // Act
        var result = UriTools.IsValidUri(uri);
        
        // Assert
        Assert.Equal(expected, result);
    }
    
    [Fact]
    public void TryParseUri_ShouldParseValidUri()
    {
        // Arrange
        var uriString = "https://user:pass@example.com:8080/path?query=value#fragment";
        
        // Act
        var result = UriTools.TryParseUri(uriString, out var uri);
        
        // Assert
        Assert.True(result);
        Assert.NotNull(uri);
        Assert.Equal("https", uri.Scheme);
        Assert.Equal("example.com", uri.Host);
        Assert.Equal(8080, uri.Port);
        Assert.Equal("/path", uri.AbsolutePath);
        Assert.Equal("?query=value", uri.Query);
        Assert.Equal("#fragment", uri.Fragment);
    }
    
    [Fact]
    public void TryParseUri_ShouldFailForInvalidUri()
    {
        // Arrange
        var invalidUri = ""; // Empty string will fail
        
        // Act
        var result = UriTools.TryParseUri(invalidUri, out var uri);
        
        // Assert
        Assert.False(result);
        Assert.Null(uri);
    }
    
    [Fact]
    public void GetUriComponents_ShouldReturnCorrectComponents()
    {
        // Arrange
        var uri = new Uri("https://user:pass@example.com:8080/path/to/resource?query=value&param=123#fragment");
        
        // Act
        var components = UriTools.GetUriComponents(uri);
        
        // Assert
        Assert.Equal("https", components.Scheme);
        Assert.Equal("example.com", components.Host);
        Assert.Equal(8080, components.Port);
        Assert.Equal("/path/to/resource", components.Path);
        Assert.Equal("?query=value&param=123", components.Query);
        Assert.Equal("#fragment", components.Fragment);
        Assert.Equal("example.com:8080", components.Authority);
    }
    
    [Fact]
    public void CanonicalizePath_ShouldNormalizePath()
    {
        // Arrange
        var path = "/path/../to/./resource/";
        
        // Act
        var result = UriTools.CanonicalizePath(path);
        
        // Assert
        Assert.Equal("/to/resource/", result);
    }
    
    [Theory]
    [InlineData("/path/../to/resource", "/to/resource")]
    [InlineData("/path/./to/resource", "/path/to/resource")]
    [InlineData("/../path/to/resource", "/path/to/resource")]
    [InlineData("/path/to/resource/../..", "/path")]
    [InlineData("/", "/")]
    public void CanonicalizePath_ShouldHandleVariousPaths(string input, string expected)
    {
        // Act
        var result = UriTools.CanonicalizePath(input);
        
        // Assert
        Assert.Equal(expected, result);
    }
}

public class ProtocolHandlerTests
{
    [Fact]
    public void HttpProtocolHandler_ShouldHandleHttpAndHttps()
    {
        // Arrange
        using var httpClient = new HttpClient();
        var handler = new HttpProtocolHandler(httpClient);
        var httpUri = new Uri("http://example.com");
        var httpsUri = new Uri("https://example.com");
        var ftpUri = new Uri("ftp://example.com");
        
        // Act & Assert
        Assert.True(handler.CanHandle(httpUri));
        Assert.True(handler.CanHandle(httpsUri));
        Assert.False(handler.CanHandle(ftpUri));
    }
    
    [Fact]
    public async Task HttpProtocolHandler_ShouldExecuteSuccessfully()
    {
        // Arrange
        using var httpClient = new HttpClient();
        var handler = new HttpProtocolHandler(httpClient);
        var uri = new Uri("https://httpbin.org/get");
        
        // Act
        var result = await handler.ExecuteAsync(uri);
        
        // Assert
        Assert.NotNull(result);
        Assert.Contains("StatusCode", result);
    }
    
    [Fact]
    public void FileProtocolHandler_ShouldHandleFileScheme()
    {
        // Arrange
        var handler = new FileProtocolHandler();
        var fileUri = new Uri("file:///C:/temp/test.txt");
        var httpUri = new Uri("http://example.com");
        
        // Act & Assert
        Assert.True(handler.CanHandle(fileUri));
        Assert.False(handler.CanHandle(httpUri));
    }
    
    [Fact]
    public async Task FileProtocolHandler_ShouldExecuteForNonExistentFile()
    {
        // Arrange
        var handler = new FileProtocolHandler();
        var uri = new Uri("file:///C:/nonexistent/file.txt");
        
        // Act
        var result = await handler.ExecuteAsync(uri);
        
        // Assert
        Assert.NotNull(result);
        Assert.Contains("File not found", result);
    }
    
    [Fact]
    public void CustomSchemeHandler_ShouldHandleCustomScheme()
    {
        // Arrange
        var handler = new CustomSchemeHandler();
        var customUri = new Uri("custom://action/data");
        var httpUri = new Uri("http://example.com");
        
        // Act & Assert
        Assert.True(handler.CanHandle(customUri));
        Assert.False(handler.CanHandle(httpUri));
    }
    
    [Fact]
    public async Task CustomSchemeHandler_ShouldExecuteSuccessfully()
    {
        // Arrange
        var handler = new CustomSchemeHandler();
        var uri = new Uri("custom://test/action");
        
        // Act
        var result = await handler.ExecuteAsync(uri);
        
        // Assert
        Assert.NotNull(result);
        Assert.Contains("Handled custom scheme", result);
        Assert.Contains("test", result);
        Assert.Contains("action", result);
    }
}

public class UriInfoTests
{
    [Fact]
    public void UriInfo_ShouldInitializeCorrectly()
    {
        // Arrange & Act
        var components = new UriInfo
        {
            Scheme = "https",
            Host = "example.com",
            Port = 443,
            Path = "/path",
            Query = "?query=value",
            Fragment = "#fragment",
            Authority = "example.com:443"
        };
        
        // Assert
        Assert.Equal("https", components.Scheme);
        Assert.Equal("example.com", components.Host);
        Assert.Equal(443, components.Port);
        Assert.Equal("/path", components.Path);
        Assert.Equal("?query=value", components.Query);
        Assert.Equal("#fragment", components.Fragment);
        Assert.Equal("example.com:443", components.Authority);
    }
}
