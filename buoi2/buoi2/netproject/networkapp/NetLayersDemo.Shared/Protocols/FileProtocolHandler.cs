using NetLayersDemo.Shared.Abstractions;

namespace NetLayersDemo.Shared.Protocols;

/// <summary>
/// Protocol handler for file:// scheme
/// </summary>
public class FileProtocolHandler : IProtocolHandler
{
    public string ProtocolName => "File";

    public bool CanHandle(Uri uri)
    {
        ArgumentNullException.ThrowIfNull(uri);
        return uri.Scheme.Equals("file", StringComparison.OrdinalIgnoreCase);
    }

    public async Task<string> ExecuteAsync(Uri uri, CancellationToken cancellationToken = default)
    {
        ArgumentNullException.ThrowIfNull(uri);

        if (!CanHandle(uri))
            throw new NotSupportedException($"URI scheme '{uri.Scheme}' is not supported by this handler");

        try
        {
            var filePath = uri.LocalPath;
            
            if (!File.Exists(filePath))
            {
                return $"File not found: {filePath}";
            }

            var fileInfo = new FileInfo(filePath);
            var content = await File.ReadAllTextAsync(filePath, cancellationToken);

            var result = new
            {
                FilePath = filePath,
                Exists = true,
                Size = fileInfo.Length,
                CreatedUtc = fileInfo.CreationTimeUtc,
                ModifiedUtc = fileInfo.LastWriteTimeUtc,
                Extension = fileInfo.Extension,
                ContentLength = content.Length,
                ContentPreview = content.Length > 500 ? content[..500] + "..." : content
            };

            return System.Text.Json.JsonSerializer.Serialize(result, new System.Text.Json.JsonSerializerOptions 
            { 
                WriteIndented = true 
            });
        }
        catch (UnauthorizedAccessException)
        {
            return "Access denied to the file";
        }
        catch (DirectoryNotFoundException)
        {
            return "Directory not found";
        }
        catch (FileNotFoundException)
        {
            return "File not found";
        }
        catch (Exception ex)
        {
            return $"Error reading file: {ex.Message}";
        }
    }
}