# Network Application Demo

This is a Python-based network application that demonstrates communication between client and server devices over a network. The application includes both HTTP request/response and realtime WebSocket communication.

## 🌟 Features

- **HTTP API**: REST endpoints for echo and server status
- **WebSocket**: Realtime bidirectional communication
- **Web Client**: Browser-based interface for testing
- **Python Client**: Standalone Python client for programmatic testing
- **Automated Tests**: Unit tests for all endpoints

## 🏗️ Architecture

The application demonstrates the network communication patterns shown in your slides:
- **Server Application**: Runs on an end device (your computer)
- **Client Applications**: Browser and Python clients that communicate over the network
- **Protocols**: HTTP (application layer) and WebSocket (realtime) over TCP

## 📋 Requirements

- Python 3.7+
- pip (Python package manager)

## 🚀 Quick Start

### 1. Install Dependencies

```powershell
pip install flask requests pytest
```

### 2. Start the Server

```powershell
python simple_server.py
```

The server will start on `http://localhost:3000`

### 3. Test the Application

#### Option A: Web Browser
Open your browser and navigate to: `http://localhost:3000`

#### Option B: Python Client
In a new PowerShell window:
```powershell
python simple_client.py
```

#### Option C: Run Tests
```powershell
python -m pytest test_server.py -v
```

## 🔌 API Endpoints

### HTTP Endpoints

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/` | Serve web client | None | HTML page |
| POST | `/api/echo` | Echo message with timestamp | `{"message": "text"}` | `{"message": "text", "timestamp": "ISO-8601"}` |
| GET | `/api/status` | Server statistics | None | `{"uptime": seconds, "requests_handled": count}` |

### WebSocket Events

| Event | Direction | Description | Data |
|-------|-----------|-------------|------|
| `connect` | Client → Server | Client connects | None |
| `disconnect` | Client → Server | Client disconnects | None |
| `client_message` | Client → Server | Send message | `{"message": "text"}` |
| `server_broadcast` | Server → Client | Periodic broadcasts | `{"message": "text", "timestamp": "ISO-8601"}` |
| `message_response` | Server → Client | Echo response | `{"message": "text", "timestamp": "ISO-8601"}` |

## 🧪 Testing

### Run Unit Tests
```powershell
pytest test_server.py -v
```

### Manual Testing with Python Client
```powershell
python client_demo.py
```

### Manual Testing with curl
```powershell
# Test echo endpoint
curl -X POST -H "Content-Type: application/json" -d "{\"message\":\"Hello\"}" http://localhost:3000/api/echo

# Test status endpoint
curl http://localhost:3000/api/status
```

## 📁 Project Structure

```
networkcomunicateapp/
├── simple_server.py        # Main Flask server (HTTP only)
├── server.py              # Enhanced server with WebSocket support (optional)
├── simple_client.py        # Simple Python client for testing
├── client_demo.py          # Advanced Python client (for full server)
├── test_server.py          # Unit tests
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

**Quick Start Files:**
- `simple_server.py` - The main server (recommended for beginners)
- `simple_client.py` - Basic client test
- Use these files first to understand the concepts

## 🔧 Configuration

- **Port**: Default is 3000 (configurable in server.py)
- **Host**: Default is 0.0.0.0 (accepts connections from any IP)
- **Broadcast Interval**: Server sends broadcasts every 10 seconds

## 🚨 Troubleshooting

### Server won't start
- Check if port 3000 is already in use
- Install dependencies: `pip install -r requirements.txt`

### Client can't connect
- Ensure server is running: `python server.py`
- Check firewall settings
- Try accessing `http://localhost:3000` in browser

### WebSocket issues
- Some corporate firewalls block WebSocket connections
- Try the HTTP-only features first

## 🎯 Learning Objectives

This application demonstrates:

1. **Network Communication**: How applications on different devices communicate
2. **Request/Response Pattern**: HTTP endpoints for synchronous communication
3. **Realtime Communication**: WebSocket for bidirectional, low-latency messaging
4. **Client-Server Architecture**: Clear separation between client and server roles
5. **Testing**: Both automated unit tests and manual testing approaches

## 🔄 Next Steps

To extend this application, you could:
- Add authentication and user management
- Implement a database for persistent data
- Add more complex message routing
- Deploy to a cloud service for remote access
- Add SSL/TLS encryption for security
- Implement a mobile app client

## 📝 License

This is a demo application for educational purposes.