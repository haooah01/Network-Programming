using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using Newtonsoft.Json.Linq;

namespace TcpChatApp;

public partial class Form1 : Form
{
    private TcpListener? server;
    private TcpClient? client;
    private Thread? serverThread;
    private Thread? clientThread;
    private bool isServerRunning = false;
    private bool isConnected = false;
    private readonly object lockObj = new();

    // Controls
    private TextBox serverHostText;
    private TextBox serverPortText;
    private Button startServerBtn;
    private Button stopServerBtn;
    private TextBox serverLogText;

    private TextBox clientHostText;
    private TextBox clientPortText;
    private TextBox clientNameText;
    private Button connectBtn;
    private Button disconnectBtn;

    private TextBox chatText;
    private TextBox messageText;
    private Button sendBtn;

    private Button sendFileBtn;
    private ProgressBar fileProgressBar;
    private ListBox receivedFilesList;
    private Button refreshFilesBtn;

    public Form1()
    {
        InitializeComponent();
        InitializeControls();
    }

    private void InitializeControls()
    {
        this.Text = "TCP Chat & File Transfer - Modern UI";
        this.Size = new Size(1200, 800);
        this.BackColor = Color.FromArgb(240, 240, 240);
        this.Font = new Font("Segoe UI", 9);

        // Main layout
        var mainTable = new TableLayoutPanel
        {
            Dock = DockStyle.Fill,
            ColumnCount = 2,
            RowCount = 2,
            ColumnStyles = { new ColumnStyle(SizeType.Percent, 70), new ColumnStyle(SizeType.Percent, 30) },
            RowStyles = { new RowStyle(SizeType.Absolute, 200), new RowStyle(SizeType.Percent, 100) }
        };
        this.Controls.Add(mainTable);

        // Server controls
        var serverGroup = new GroupBox
        {
            Text = "Server Control",
            Dock = DockStyle.Fill,
            Font = new Font("Segoe UI", 10, FontStyle.Bold),
            BackColor = Color.White,
            ForeColor = Color.DarkBlue
        };
        mainTable.Controls.Add(serverGroup, 0, 0);

        var serverLayout = new TableLayoutPanel
        {
            Dock = DockStyle.Fill,
            ColumnCount = 4,
            RowCount = 3
        };
        serverGroup.Controls.Add(serverLayout);

        var hostLabel = new Label { Text = "Host:", AutoSize = true, Font = new Font("Segoe UI", 9) };
        serverHostText = new TextBox { Text = "0.0.0.0", Dock = DockStyle.Fill, Font = new Font("Segoe UI", 9) };
        var portLabel = new Label { Text = "Port:", AutoSize = true, Font = new Font("Segoe UI", 9) };
        serverPortText = new TextBox { Text = "5050", Dock = DockStyle.Fill, Font = new Font("Segoe UI", 9) };
        startServerBtn = new Button { Text = "Start Server", Dock = DockStyle.Fill, BackColor = Color.LightGreen, Font = new Font("Segoe UI", 9, FontStyle.Bold) };
        startServerBtn.Click += StartServerBtn_Click;
        stopServerBtn = new Button { Text = "Stop Server", Dock = DockStyle.Fill, BackColor = Color.LightCoral, Enabled = false, Font = new Font("Segoe UI", 9, FontStyle.Bold) };
        stopServerBtn.Click += StopServerBtn_Click;
        serverLogText = new TextBox { Multiline = true, ScrollBars = ScrollBars.Vertical, Dock = DockStyle.Fill, ReadOnly = true, BackColor = Color.Black, ForeColor = Color.LightGreen, Font = new Font("Consolas", 8) };

        serverLayout.Controls.Add(hostLabel, 0, 0);
        serverLayout.Controls.Add(serverHostText, 1, 0);
        serverLayout.Controls.Add(portLabel, 2, 0);
        serverLayout.Controls.Add(serverPortText, 3, 0);
        serverLayout.Controls.Add(startServerBtn, 0, 1);
        serverLayout.Controls.Add(stopServerBtn, 1, 1);
        serverLayout.SetColumnSpan(serverLogText, 4);
        serverLayout.Controls.Add(serverLogText, 0, 2);

        // Client controls
        var clientGroup = new GroupBox
        {
            Text = "Client Connection",
            Dock = DockStyle.Fill,
            Font = new Font("Segoe UI", 10, FontStyle.Bold),
            BackColor = Color.White,
            ForeColor = Color.DarkBlue
        };
        mainTable.Controls.Add(clientGroup, 1, 0);

        var clientLayout = new TableLayoutPanel
        {
            Dock = DockStyle.Fill,
            ColumnCount = 3,
            RowCount = 3
        };
        clientGroup.Controls.Add(clientLayout);

        var chostLabel = new Label { Text = "Host:", AutoSize = true, Font = new Font("Segoe UI", 9) };
        clientHostText = new TextBox { Text = "127.0.0.1", Dock = DockStyle.Fill, Font = new Font("Segoe UI", 9) };
        var cportLabel = new Label { Text = "Port:", AutoSize = true, Font = new Font("Segoe UI", 9) };
        clientPortText = new TextBox { Text = "5050", Dock = DockStyle.Fill, Font = new Font("Segoe UI", 9) };
        var nameLabel = new Label { Text = "Name:", AutoSize = true, Font = new Font("Segoe UI", 9) };
        clientNameText = new TextBox { Text = "user", Dock = DockStyle.Fill, Font = new Font("Segoe UI", 9) };
        connectBtn = new Button { Text = "Connect", Dock = DockStyle.Fill, BackColor = Color.LightBlue, Font = new Font("Segoe UI", 9, FontStyle.Bold) };
        connectBtn.Click += ConnectBtn_Click;
        disconnectBtn = new Button { Text = "Disconnect", Dock = DockStyle.Fill, BackColor = Color.LightCoral, Enabled = false, Font = new Font("Segoe UI", 9, FontStyle.Bold) };
        disconnectBtn.Click += DisconnectBtn_Click;

        clientLayout.Controls.Add(chostLabel, 0, 0);
        clientLayout.Controls.Add(clientHostText, 1, 0);
        clientLayout.Controls.Add(cportLabel, 0, 1);
        clientLayout.Controls.Add(clientPortText, 1, 1);
        clientLayout.Controls.Add(nameLabel, 0, 2);
        clientLayout.Controls.Add(clientNameText, 1, 2);
        clientLayout.Controls.Add(connectBtn, 0, 3);
        clientLayout.Controls.Add(disconnectBtn, 1, 3);

        // Chat
        var chatGroup = new GroupBox
        {
            Text = "Chat",
            Dock = DockStyle.Fill,
            Font = new Font("Segoe UI", 10, FontStyle.Bold),
            BackColor = Color.White,
            ForeColor = Color.DarkBlue
        };
        mainTable.Controls.Add(chatGroup, 0, 1);

        var chatLayout = new TableLayoutPanel
        {
            Dock = DockStyle.Fill,
            RowCount = 2,
            ColumnCount = 2,
            RowStyles = { new RowStyle(SizeType.Percent, 80), new RowStyle(SizeType.Absolute, 40) }
        };
        chatGroup.Controls.Add(chatLayout);

        chatText = new TextBox { Multiline = true, ScrollBars = ScrollBars.Vertical, Dock = DockStyle.Fill, ReadOnly = true, BackColor = Color.White, Font = new Font("Segoe UI", 9) };
        chatLayout.Controls.Add(chatText, 0, 0);
        chatLayout.SetColumnSpan(chatText, 2);

        messageText = new TextBox { Dock = DockStyle.Fill, Font = new Font("Segoe UI", 9) };
        sendBtn = new Button { Text = "Send", Dock = DockStyle.Fill, BackColor = Color.LightGreen, Enabled = false, Font = new Font("Segoe UI", 9, FontStyle.Bold) };
        sendBtn.Click += SendBtn_Click;

        chatLayout.Controls.Add(messageText, 0, 1);
        chatLayout.Controls.Add(sendBtn, 1, 1);

        // File and received
        var fileGroup = new GroupBox
        {
            Text = "Files",
            Dock = DockStyle.Fill,
            Font = new Font("Segoe UI", 10, FontStyle.Bold),
            BackColor = Color.White,
            ForeColor = Color.DarkBlue
        };
        mainTable.Controls.Add(fileGroup, 1, 1);

        var fileLayout = new TableLayoutPanel
        {
            Dock = DockStyle.Fill,
            RowCount = 4,
            ColumnCount = 1
        };
        fileGroup.Controls.Add(fileLayout);

        sendFileBtn = new Button { Text = "Send File", Dock = DockStyle.Fill, BackColor = Color.LightYellow, Enabled = false, Font = new Font("Segoe UI", 9, FontStyle.Bold) };
        sendFileBtn.Click += SendFileBtn_Click;
        fileProgressBar = new ProgressBar { Dock = DockStyle.Fill, Visible = false };

        receivedFilesList = new ListBox { Dock = DockStyle.Fill, Font = new Font("Segoe UI", 9) };
        refreshFilesBtn = new Button { Text = "Refresh Files", Dock = DockStyle.Fill, BackColor = Color.LightGray, Font = new Font("Segoe UI", 9, FontStyle.Bold) };
        refreshFilesBtn.Click += RefreshFilesBtn_Click;

        fileLayout.Controls.Add(sendFileBtn, 0, 0);
        fileLayout.Controls.Add(fileProgressBar, 0, 1);
        fileLayout.Controls.Add(receivedFilesList, 0, 2);
        fileLayout.Controls.Add(refreshFilesBtn, 0, 3);

        RefreshFiles();
    }

    private void StartServerBtn_Click(object sender, EventArgs e)
    {
        try
        {
            var host = serverHostText.Text;
            var port = int.Parse(serverPortText.Text);
            server = new TcpListener(IPAddress.Parse(host), port);
            server.Start();
            isServerRunning = true;
            startServerBtn.Enabled = false;
            stopServerBtn.Enabled = true;
            LogServer($"Server started on {host}:{port}");
            serverThread = new Thread(ServerLoop) { IsBackground = true };
            serverThread.Start();
        }
        catch (Exception ex)
        {
            MessageBox.Show($"Server start error: {ex.Message}");
        }
    }

    private void StopServerBtn_Click(object sender, EventArgs e)
    {
        isServerRunning = false;
        server?.Stop();
        startServerBtn.Enabled = true;
        stopServerBtn.Enabled = false;
        LogServer("Server stopped");
    }

    private void ServerLoop()
    {
        while (isServerRunning)
        {
            try
            {
                var clientSocket = server.AcceptTcpClient();
                LogServer($"Client connected: {clientSocket.Client.RemoteEndPoint}");
                var clientThread = new Thread(() => HandleClient(clientSocket)) { IsBackground = true };
                clientThread.Start();
            }
            catch (Exception ex)
            {
                if (isServerRunning)
                    LogServer($"Server error: {ex.Message}");
            }
        }
    }

    private void HandleClient(TcpClient tcpClient)
    {
        var stream = tcpClient.GetStream();
        var buffer = new byte[1024];
        while (tcpClient.Connected)
        {
            try
            {
                var msg = ReceiveMessage(stream);
                if (msg == null) break;
                var type = msg["type"]?.ToString();
                if (type == "chat")
                {
                    var chatMsg = $"[{msg["from"]}]: {msg["text"]}";
                    BroadcastMessage(msg, tcpClient);
                    Invoke(() => LogChat(chatMsg));
                }
                else if (type == "file_meta")
                {
                    // Handle file receive
                    var filename = msg["filename"]?.ToString();
                    var size = (long)msg["size"];
                    var sha256 = msg["sha256"]?.ToString();
                    LogServer($"Receiving file: {filename}");
                    SendAck(stream, true, msg["corr_id"]?.ToString());
                    var fileData = ReceiveFile(stream, size);
                    if (ComputeSha256(fileData) == sha256)
                    {
                        File.WriteAllBytes(filename, fileData);
                        LogServer($"File {filename} saved");
                        SendAck(stream, true, msg["corr_id"]?.ToString());
                        Invoke(() => RefreshFiles());
                    }
                    else
                    {
                        LogServer($"File {filename} hash mismatch");
                        SendAck(stream, false, msg["corr_id"]?.ToString(), "Hash mismatch");
                    }
                }
            }
            catch (Exception ex)
            {
                LogServer($"Client error: {ex.Message}");
                break;
            }
        }
        tcpClient.Close();
    }

    private void BroadcastMessage(JObject msg, TcpClient excludeClient)
    {
        // For simplicity, not implemented full broadcast
    }

    private void ConnectBtn_Click(object sender, EventArgs e)
    {
        try
        {
            client = new TcpClient();
            client.Connect(clientHostText.Text, int.Parse(clientPortText.Text));
            isConnected = true;
            connectBtn.Enabled = false;
            disconnectBtn.Enabled = true;
            sendBtn.Enabled = true;
            sendFileBtn.Enabled = true;
            LogChat($"Connected as {clientNameText.Text}");
            clientThread = new Thread(ClientLoop) { IsBackground = true };
            clientThread.Start();
        }
        catch (Exception ex)
        {
            MessageBox.Show($"Connect error: {ex.Message}");
        }
    }

    private void DisconnectBtn_Click(object sender, EventArgs e)
    {
        isConnected = false;
        client?.Close();
        connectBtn.Enabled = true;
        disconnectBtn.Enabled = false;
        sendBtn.Enabled = false;
        sendFileBtn.Enabled = false;
        LogChat("Disconnected");
    }

    private void ClientLoop()
    {
        var stream = client.GetStream();
        while (isConnected)
        {
            try
            {
                var msg = ReceiveMessage(stream);
                if (msg == null) break;
                var type = msg["type"]?.ToString();
                if (type == "chat")
                {
                    Invoke(() => LogChat($"[{msg["from"]}]: {msg["text"]}"));
                }
                else if (type == "ack")
                {
                    // Handle ack
                }
            }
            catch (Exception ex)
            {
                if (isConnected)
                    Invoke(() => LogChat($"Read error: {ex.Message}"));
                break;
            }
        }
    }

    private void SendBtn_Click(object sender, EventArgs e)
    {
        var text = messageText.Text.Trim();
        if (!string.IsNullOrEmpty(text))
        {
            var msg = new JObject
            {
                ["type"] = "chat",
                ["text"] = text,
                ["from"] = clientNameText.Text,
                ["room"] = "default"
            };
            SendMessage(client.GetStream(), msg);
            messageText.Clear();
            LogChat($"You: {text}");
        }
    }

    private void SendFileBtn_Click(object sender, EventArgs e)
    {
        var openFileDialog = new OpenFileDialog();
        if (openFileDialog.ShowDialog() == DialogResult.OK)
        {
            var filename = Path.GetFileName(openFileDialog.FileName);
            var fileData = File.ReadAllBytes(openFileDialog.FileName);
            var sha256 = ComputeSha256(fileData);
            var corrId = Guid.NewGuid().ToString();
            var meta = new JObject
            {
                ["type"] = "file_meta",
                ["filename"] = filename,
                ["size"] = fileData.Length,
                ["sha256"] = sha256,
                ["from"] = clientNameText.Text,
                ["corr_id"] = corrId
            };
            SendMessage(client.GetStream(), meta);
            LogChat($"Starting to send {filename}");

            var ack = ReceiveMessage(client.GetStream());
            if (ack?["ok"]?.ToObject<bool>() == true)
            {
                SendFileChunks(client.GetStream(), fileData, corrId);
                var finalAck = ReceiveMessage(client.GetStream());
                if (finalAck?["ok"]?.ToObject<bool>() == true)
                {
                    LogChat($"File {filename} sent successfully");
                }
                else
                {
                    LogChat($"File send failed: {finalAck?["error"]}");
                }
            }
            else
            {
                LogChat($"File send failed: {ack?["error"]}");
            }
        }
    }

    private void SendFileChunks(NetworkStream stream, byte[] data, string corrId)
    {
        const int chunkSize = 65536;
        var offset = 0;
        while (offset < data.Length)
        {
            var chunk = data.Skip(offset).Take(chunkSize).ToArray();
            var b64 = Convert.ToBase64String(chunk);
            var chunkMsg = new JObject
            {
                ["type"] = "file_chunk",
                ["offset"] = offset,
                ["data"] = b64,
                ["from"] = clientNameText.Text,
                ["room"] = "default",
                ["corr_id"] = corrId
            };
            SendMessage(stream, chunkMsg);
            offset += chunk.Length;
        }
    }

    private void RefreshFilesBtn_Click(object sender, EventArgs e)
    {
        RefreshFiles();
    }

    private void RefreshFiles()
    {
        receivedFilesList.Items.Clear();
        try
        {
            var files = Directory.GetFiles(".", "*.*").Where(f => !f.EndsWith(".exe") && !f.EndsWith(".dll") && !f.EndsWith(".cs")).Select(Path.GetFileName);
            foreach (var file in files)
            {
                receivedFilesList.Items.Add(file);
            }
        }
        catch { }
    }

    private void LogServer(string msg)
    {
        if (InvokeRequired)
            Invoke(() => serverLogText.AppendText(msg + Environment.NewLine));
        else
            serverLogText.AppendText(msg + Environment.NewLine);
    }

    private void LogChat(string msg)
    {
        if (InvokeRequired)
            Invoke(() => chatText.AppendText(msg + Environment.NewLine));
        else
            chatText.AppendText(msg + Environment.NewLine);
    }

    private void SendMessage(NetworkStream stream, JObject msg)
    {
        lock (lockObj)
        {
            var json = msg.ToString();
            var data = Encoding.UTF8.GetBytes(json);
            var length = BitConverter.GetBytes(data.Length);
            stream.Write(length, 0, 4);
            stream.Write(data, 0, data.Length);
        }
    }

    private JObject? ReceiveMessage(NetworkStream stream)
    {
        var lengthBytes = new byte[4];
        var read = stream.Read(lengthBytes, 0, 4);
        if (read < 4) return null;
        var length = BitConverter.ToInt32(lengthBytes);
        var data = new byte[length];
        read = 0;
        while (read < length)
        {
            var r = stream.Read(data, read, length - read);
            if (r == 0) return null;
            read += r;
        }
        var json = Encoding.UTF8.GetString(data);
        return JObject.Parse(json);
    }

    private byte[] ReceiveFile(NetworkStream stream, long size)
    {
        using var ms = new MemoryStream();
        long received = 0;
        while (received < size)
        {
            var msg = ReceiveMessage(stream);
            if (msg?["type"]?.ToString() == "file_chunk")
            {
                var chunkData = Convert.FromBase64String(msg["data"]?.ToString());
                ms.Write(chunkData, 0, chunkData.Length);
                received += chunkData.Length;
            }
        }
        return ms.ToArray();
    }

    private void SendAck(NetworkStream stream, bool ok, string corrId, string error = "")
    {
        var ack = new JObject
        {
            ["type"] = "ack",
            ["ok"] = ok,
            ["corr_id"] = corrId
        };
        if (!ok) ack["error"] = error;
        SendMessage(stream, ack);
    }

    private string ComputeSha256(byte[] data)
    {
        using var sha256 = System.Security.Cryptography.SHA256.Create();
        var hash = sha256.ComputeHash(data);
        return BitConverter.ToString(hash).Replace("-", "").ToLower();
    }
}
