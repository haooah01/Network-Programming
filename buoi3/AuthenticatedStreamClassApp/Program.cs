using System;
using System.IO;
using System.Net;
using System.Net.Security;
using System.Net.Sockets;
using System.Security.Authentication;
using System.Security.Cryptography;
using System.Security.Cryptography.X509Certificates;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

public record DemoOptions(int Port = 5001, bool RequireClientCertificate = false);

static class AuthenticatedStreamReporter
{
    public static void DisplayProperties(AuthenticatedStream stream)
    {
        Console.WriteLine("IsAuthenticated: {0}", stream.IsAuthenticated);
        Console.WriteLine("IsMutuallyAuthenticated: {0}", stream.IsMutuallyAuthenticated);
        Console.WriteLine("IsEncrypted: {0}", stream.IsEncrypted);
        Console.WriteLine("IsSigned: {0}", stream.IsSigned);
        Console.WriteLine("IsServer: {0}", stream.IsServer);
    }
}

public class Demo
{
    public X509Certificate2? RootCa { get; private set; }

    public X509Certificate2 CreateCertificateAuthority(string subject)
    {
        using var rsa = RSA.Create(4096);
        var req = new CertificateRequest(subject, rsa, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
        req.CertificateExtensions.Add(new X509BasicConstraintsExtension(true, false, 0, true));
        req.CertificateExtensions.Add(new X509SubjectKeyIdentifierExtension(req.PublicKey, false));
        var cert = req.CreateSelfSigned(DateTimeOffset.UtcNow.AddDays(-1), DateTimeOffset.UtcNow.AddYears(10));
        var export = cert.Export(X509ContentType.Pfx);
        RootCa = new X509Certificate2(export, (string?)null, X509KeyStorageFlags.Exportable);
        return RootCa;
    }

    public X509Certificate2 CreateSignedCertificate(string subject, X509Certificate2 issuer)
    {
        using var rsa = RSA.Create(2048);
        var req = new CertificateRequest(subject, rsa, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
        req.CertificateExtensions.Add(new X509BasicConstraintsExtension(false, false, 0, false));
        req.CertificateExtensions.Add(new X509KeyUsageExtension(X509KeyUsageFlags.DigitalSignature | X509KeyUsageFlags.KeyEncipherment, false));
        req.CertificateExtensions.Add(new X509SubjectKeyIdentifierExtension(req.PublicKey, false));

        // Create certificate signed by issuer (Root CA)
        var notBefore = DateTimeOffset.UtcNow.AddDays(-1);
        var notAfter = DateTimeOffset.UtcNow.AddYears(2);

        var serial = new byte[16];
        RandomNumberGenerator.Fill(serial);

        // Create certificate signed by issuer
        var cert = req.Create(issuer, notBefore, notAfter, serial);
        // Attach the generated private key and export as PFX so SslStream can use it
        var certWithKey = cert.CopyWithPrivateKey(rsa);
        var pfx = certWithKey.Export(X509ContentType.Pfx);
        return new X509Certificate2(pfx, (string?)null, X509KeyStorageFlags.Exportable);
    }

    public async Task RunAsync(DemoOptions options, CancellationToken ct = default)
    {
        Console.WriteLine("Starting demo: SslStream server/client. Port={0} RequireClientCert={1}", options.Port, options.RequireClientCertificate);

        // Create CA and sign server/client certs
        var ca = CreateCertificateAuthority("CN=DemoRootCA");
        using var serverCert = CreateSignedCertificate("CN=localhost-demo", ca);
        using var clientCert = CreateSignedCertificate("CN=demo-client", ca);

        int portToUse = options.Port;
        TcpListener? preListener = null;
        if (portToUse == 0)
        {
            // allocate a free port and close the listener; we'll use the port value
            preListener = new TcpListener(IPAddress.Loopback, 0);
            preListener.Start();
            portToUse = ((IPEndPoint)preListener.LocalEndpoint).Port;
            preListener.Stop();
        }

        var serverTask = RunServerAsync(portToUse, serverCert, ca, options.RequireClientCertificate, ct);
        await Task.Delay(250, ct); // brief pause
        var clientTask = RunClientAsync(portToUse, ca, options.RequireClientCertificate ? clientCert : null, ct);

        await Task.WhenAll(serverTask, clientTask);
    }

    async Task RunServerAsync(int port, X509Certificate2 serverCert, X509Certificate2 caCert, bool requireClientCert, CancellationToken ct)
    {
        var listener = new TcpListener(IPAddress.Loopback, port);
        listener.Start();
        Console.WriteLine("Server listening on 127.0.0.1:{0}", port);

        using var client = await listener.AcceptTcpClientAsync(ct);
        Console.WriteLine("Server: client connected");

        using var network = client.GetStream();
        // When requesting client certs, allow SslStream to receive them.
        using var ssl = new SslStream(network, leaveInnerStreamOpen: false, userCertificateValidationCallback: null);

        try
        {
            await ssl.AuthenticateAsServerAsync(serverCert, clientCertificateRequired: requireClientCert, enabledSslProtocols: SslProtocols.Tls12 | SslProtocols.Tls13, checkCertificateRevocation: false);
            Console.WriteLine("Server: SSL AuthenticateAsServer completed.");

            AuthenticatedStreamReporter.DisplayProperties(ssl);

            if (requireClientCert)
            {
                var remote = ssl.RemoteCertificate;
                if (remote == null)
                {
                    Console.WriteLine("Server: no client certificate presented");
                    return;
                }
                var clientCert = new X509Certificate2(remote);
                Console.WriteLine("Server: client certificate subject: {0}", clientCert.Subject);

                // Validate client cert chain against our CA
                var chain = new X509Chain();
                chain.ChainPolicy.ExtraStore.Add(caCert);
                chain.ChainPolicy.RevocationMode = X509RevocationMode.NoCheck;
                chain.ChainPolicy.VerificationFlags = X509VerificationFlags.AllowUnknownCertificateAuthority;
                var valid = chain.Build(clientCert);
                // Ensure the chain ends in our CA
                var endsInCa = false;
                foreach (var el in chain.ChainElements)
                {
                    if (el.Certificate.Thumbprint == caCert.Thumbprint) { endsInCa = true; break; }
                }
                Console.WriteLine("Server: client cert chain valid={0} endsInCa={1}", valid, endsInCa);
            }

            // Echo loop
            using var reader = new StreamReader(ssl, Encoding.UTF8, leaveOpen: true);
            using var writer = new StreamWriter(ssl, Encoding.UTF8, leaveOpen: true) { AutoFlush = true };

            var line = await reader.ReadLineAsync();
            Console.WriteLine("Server received: {0}", line);
            await writer.WriteLineAsync("Echo: " + line);
        }
        catch (Exception ex)
        {
            Console.WriteLine("Server exception: " + ex);
        }
        finally
        {
            listener.Stop();
        }
    }

    async Task RunClientAsync(int port, X509Certificate2 caCert, X509Certificate2? clientCert, CancellationToken ct)
    {
        using var tcp = new TcpClient();
        await tcp.ConnectAsync(IPAddress.Loopback, port, ct);
        Console.WriteLine("Client: connected to server");

        using var network = tcp.GetStream();
        using var ssl = new SslStream(network, leaveInnerStreamOpen: false, userCertificateValidationCallback: (sender, cert, chain, errors) =>
        {
            // Build a chain and verify it ends in our CA and that the hostname matches
            if (cert == null) return false;
            Console.WriteLine("Client: server certificate subject: " + cert.Subject);

            var serverCert = new X509Certificate2(cert);
            var localChain = new X509Chain();
            localChain.ChainPolicy.ExtraStore.Add(caCert);
            localChain.ChainPolicy.RevocationMode = X509RevocationMode.NoCheck;
            localChain.ChainPolicy.VerificationFlags = X509VerificationFlags.AllowUnknownCertificateAuthority;
            var built = localChain.Build(serverCert);

            var endsInCa = false;
            foreach (var el in localChain.ChainElements)
            {
                if (el.Certificate.Thumbprint == caCert.Thumbprint) { endsInCa = true; break; }
            }

            // Hostname check: ensure subject CN contains 'localhost'
            var cn = serverCert.GetNameInfo(X509NameType.SimpleName, false);
            var hostOk = cn?.Contains("localhost", StringComparison.OrdinalIgnoreCase) ?? false;

            Console.WriteLine("Client: chain built={0} endsInCa={1} hostOk={2}", built, endsInCa, hostOk);
            return built && endsInCa && hostOk;
        });

        try
        {
            var clientOptions = new SslClientAuthenticationOptions
            {
                TargetHost = "localhost-demo",
                EnabledSslProtocols = SslProtocols.Tls12 | SslProtocols.Tls13,
                CertificateRevocationCheckMode = X509RevocationMode.NoCheck
            };

            if (clientCert != null)
            {
                clientOptions.ClientCertificates = new X509CertificateCollection { clientCert };
            }

            await ssl.AuthenticateAsClientAsync(clientOptions, ct);

            Console.WriteLine("Client: SSL AuthenticateAsClient completed.");

            AuthenticatedStreamReporter.DisplayProperties(ssl);

            using var reader = new StreamReader(ssl, Encoding.UTF8, leaveOpen: true);
            using var writer = new StreamWriter(ssl, Encoding.UTF8, leaveOpen: true) { AutoFlush = true };

            var message = "Hello from client at " + DateTime.Now;
            await writer.WriteLineAsync(message);
            var resp = await reader.ReadLineAsync();
            Console.WriteLine("Client received: {0}", resp);
        }
        catch (Exception ex)
        {
            Console.WriteLine("Client exception: " + ex);
        }
    }
}

// CLI entry-point helper (not used when referenced from TestsRunner)
public static class Program
{
    public static async Task<int> RunMain(string[] args)
    {
        var port = 5001;
        var require = false;
        for (int i = 0; i < args.Length; i++)
        {
            var a = args[i];
            if (a == "--port" && i + 1 < args.Length && int.TryParse(args[i + 1], out var p)) { port = p; i++; }
            else if (a == "--requireClientCert") { require = true; }
            else if (a == "-h" || a == "--help") { Console.WriteLine("Usage: --port <n> --requireClientCert"); return 0; }
        }

        var demo = new Demo();
        await demo.RunAsync(new DemoOptions(port, require));
        return 0;
    }
}
