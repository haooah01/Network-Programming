using System;
using System.Diagnostics;

class Runner
{
    static int RunMainApp(string args)
    {
    // Absolute path to main project (workspace path known from context)
    var mainProj = @"d:\Documents-D\VS Code\network programming\buoi3\AuthenticatedStreamClassApp\AuthenticatedStreamClassApp.csproj";
    var solutionDir = System.IO.Path.GetDirectoryName(mainProj)!;
        var psi = new ProcessStartInfo
        {
            FileName = "dotnet",
            Arguments = $"run --project \"{mainProj}\" -- {args}",
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            UseShellExecute = false,
            WorkingDirectory = solutionDir
        };

        using var p = Process.Start(psi)!;
        p.OutputDataReceived += (s, e) => { if (e.Data != null) Console.WriteLine(e.Data); };
        p.ErrorDataReceived += (s, e) => { if (e.Data != null) Console.Error.WriteLine(e.Data); };
        p.BeginOutputReadLine();
        p.BeginErrorReadLine();
        p.WaitForExit();
        return p.ExitCode;
    }

    static int Main()
    {
        Console.WriteLine("Running external tests (launching main app)...");

        Console.WriteLine("Test1: No client cert");
        var rc1 = RunMainApp("--port 0");
        Console.WriteLine($"Test1 exit code: {rc1}");

        Console.WriteLine("Test2: Mutual TLS");
        var rc2 = RunMainApp("--port 0 --requireClientCert");
        Console.WriteLine($"Test2 exit code: {rc2}");

        if (rc1 == 0 && rc2 == 0)
        {
            Console.WriteLine("Both runs succeeded");
            return 0;
        }
        else
        {
            Console.WriteLine("One or more runs failed");
            return 1;
        }
    }
}
