# Quick Start Guide - TCP 3-Step Handshake Demo

## 🚀 ONE-COMMAND DEMO

```powershell
cd "d:\Documents-D\VS Code\network programming\3stephandshakeapp"
powershell -ExecutionPolicy Bypass -File .\run-demo.ps1
```

## 📺 What You'll See

### Step 1: Build Phase
```
Building server...
✓ tcp-server succeeded
Building client...
✓ tcp-client succeeded
```

### Step 2: Server Starts
```
[server] Listening on 127.0.0.1:21998
[server] HTTP UI listening on http://localhost:5000/
[server] {"port":21998,"ui":5000}
```

### Step 3: Client Connects
```
[Client] Connecting to 127.0.0.1:21998...
[Client] Connected                          ← TCP handshake complete!
[Client] Sent: Hello from client
[Client] Received: Hello from server...
[Client] Closing
```

### Step 4: Browser Opens
- Your default browser opens to: `http://localhost:5000/`
- You'll see live logs updating every 1.5 seconds
- Logs show connection details and message exchange

## 🎯 What Just Happened (Behind the Scenes)

### TCP 3-Step Handshake (Automatic)
```
Client                          Server
  |                               |
  |-------- SYN ----------------->|  Step 1: Client initiates
  |                               |
  |<------ SYN-ACK --------------|  Step 2: Server acknowledges
  |                               |
  |-------- ACK ----------------->|  Step 3: Client confirms
  |                               |
  |=== CONNECTION ESTABLISHED ===|
  |                               |
  |-- "Hello from client" ------->|  Application data flows
  |                               |
  |<- "Hello from server" --------|  Response sent
  |                               |
  |-------- FIN ----------------->|  Connection closes
```

## 🧪 Testing

```powershell
cd tcp-tests
dotnet test
```

**Expected Output:**
```
Test summary: total: 1, failed: 0, succeeded: 1 ✓
```

## 🛑 Stop Server

If server is running in background:
```powershell
powershell -ExecutionPolicy Bypass -File .\stop-server.ps1
```

Or manually find and kill:
```powershell
Get-Process | Where-Object { $_.ProcessName -like '*tcp-server*' } | Stop-Process -Force
```

## 📁 Files Created

```
✓ tcp-server/Program.cs          - TCP server + HTTP UI
✓ tcp-client/Program.cs          - TCP client
✓ ui/index.html                  - Web log viewer
✓ tcp-tests/TcpIntegrationTests.cs - xUnit tests
✓ run-demo.ps1                   - Automated demo
✓ stop-server.ps1                - Cleanup script
✓ README.md                      - Full documentation
✓ SUMMARY.md                     - Technical details
✓ QUICKSTART.md                  - This file
```

## ❓ Common Questions

**Q: What port does the server use?**  
A: OS assigns an ephemeral port (random free port). The server prints it to stdout.

**Q: Can I run this multiple times?**  
A: Yes! Each run gets a new ephemeral port, so no conflicts.

**Q: How do I see server logs?**  
A: Three ways:
1. Check the terminal where server is running
2. Open the web UI at http://localhost:5000/
3. Run `run-demo.ps1` which shows server stdout

**Q: Why do I see "file is locked" errors?**  
A: A previous server process is still running. Run `stop-server.ps1` to clean up.

**Q: Can I use a specific port?**  
A: Yes, modify the server code to use a fixed port instead of 0 (ephemeral).

## 🎓 Next Steps

1. **Explore the code**: Open `tcp-server/Program.cs` and `tcp-client/Program.cs`
2. **Modify the messages**: Change what client/server send
3. **Add features**: Try adding multiple client support, chat functionality, etc.
4. **Learn more**: Read `SUMMARY.md` for technical implementation details

## 💡 Tips

- Keep the web UI open while running multiple demos to watch logs accumulate
- The server accepts ONE connection then exits (by design for demo simplicity)
- Logs are kept in memory (last 200 entries) and cleared on server restart
- All communication happens on localhost (127.0.0.1) - secure and fast

---

**Ready?** Run this now:
```powershell
powershell -ExecutionPolicy Bypass -File .\run-demo.ps1
```

Enjoy! 🎉
