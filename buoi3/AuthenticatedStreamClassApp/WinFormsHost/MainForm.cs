using System;
using System.IO;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace WinFormsHost;

public partial class MainForm : Form
{
    private CancellationTokenSource? _cts;
    private TextWriter? _originalConsoleOut;
    private bool _isRunning;

    public MainForm()
    {
        InitializeComponent();
        progressBar.Style = ProgressBarStyle.Blocks;
    }

    private async void startButton_Click(object? sender, EventArgs e)
    {
        if (_isRunning)
        {
            return;
        }

        _isRunning = true;
        ToggleUi(running: true);
        AppendLine("Launching authenticated stream demo...");

        _cts = new CancellationTokenSource();
        _originalConsoleOut = Console.Out;
        var uiWriter = new UiTextWriter(AppendLine);
        Console.SetOut(uiWriter);

        var args = requireClientCertCheckBox.Checked
            ? new[] { "--port", "0", "--requireClientCert" }
            : new[] { "--port", "0" };

        try
        {
            await Task.Run(async () =>
            {
                try
                {
                    _ = await global::Program.RunMain(args);
                }
                catch (OperationCanceledException)
                {
                    AppendLine("Demo cancelled.");
                }
            }, _cts.Token);

            AppendLine("Demo completed.");
        }
        catch (Exception ex)
        {
            AppendLine("Unexpected error: " + ex.Message);
        }
        finally
        {
            Console.SetOut(_originalConsoleOut ?? TextWriter.Null);
            _originalConsoleOut = null;
            _cts?.Dispose();
            _cts = null;
            ToggleUi(running: false);
            _isRunning = false;
        }
    }

    private void ToggleUi(bool running)
    {
        if (InvokeRequired)
        {
            BeginInvoke(() => ToggleUi(running));
            return;
        }

        startButton.Enabled = !running;
        requireClientCertCheckBox.Enabled = !running;
        progressBar.Style = running ? ProgressBarStyle.Marquee : ProgressBarStyle.Blocks;
    }

    private void AppendLine(string message)
    {
        if (InvokeRequired)
        {
            BeginInvoke(() => AppendLine(message));
            return;
        }

        outputTextBox.AppendText($"[{DateTime.Now:T}] {message}{Environment.NewLine}");
    }

    private sealed class UiTextWriter : TextWriter
    {
        private readonly Action<string> _write;

        public UiTextWriter(Action<string> write) => _write = write;

        public override Encoding Encoding => Encoding.UTF8;

        public override void WriteLine(string? value)
        {
            if (value is not null)
            {
                _write(value);
            }
        }
    }
}
