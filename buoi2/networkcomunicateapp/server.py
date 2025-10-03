from flask import Flask, request, jsonify, render_template_string
import time
import json
from datetime import datetime

# Try to import flask-socketio, but make it optional
try:
    from flask_socketio import SocketIO, emit
    SOCKETIO_AVAILABLE = True
except ImportError:
    SOCKETIO_AVAILABLE = False
    print("⚠️  flask-socketio not available, WebSocket features disabled")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'network-demo-secret'

# Initialize SocketIO only if available
if SOCKETIO_AVAILABLE:
    socketio = SocketIO(app, cors_allowed_origins="*")
else:
    socketio = None

# Server statistics
server_stats = {
    'start_time': time.time(),
    'requests_handled': 0
}

# HTML template for the client interface
CLIENT_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Network Application Demo</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.2/socket.io.js"></script>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        .output { background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 3px; }
        button { padding: 8px 16px; margin: 5px; cursor: pointer; }
        input[type="text"] { padding: 8px; margin: 5px; width: 200px; }
        .realtime-messages { max-height: 200px; overflow-y: auto; }
    </style>
</head>
<body>
    <h1>🌐 Network Application Demo</h1>
    <p>This application demonstrates network communication between client and server devices.</p>
    
    <!-- HTTP Request/Response Section -->
    <div class="section">
        <h2>📡 HTTP Request/Response</h2>
        <div>
            <input type="text" id="messageInput" placeholder="Enter message" value="Hello, Network!">
            <button onclick="sendEcho()">Send Echo Request</button>
            <button onclick="getStatus()">Get Server Status</button>
        </div>
        <div class="output" id="httpOutput">HTTP responses will appear here...</div>
    </div>
    
    <!-- WebSocket Realtime Section -->
    <div class="section">
        <h2>⚡ Realtime Communication (WebSocket)</h2>
        <div>
            <input type="text" id="realtimeInput" placeholder="Realtime message">
            <button onclick="sendRealtimeMessage()">Send Realtime</button>
            <button onclick="connectSocket()" id="connectBtn">Connect</button>
            <button onclick="disconnectSocket()" id="disconnectBtn" disabled>Disconnect</button>
        </div>
        <div class="output realtime-messages" id="realtimeOutput">
            <div>WebSocket messages will appear here...</div>
        </div>
    </div>

    <script>
        let socket = null;
        let isConnected = false;

        // HTTP Echo Request
        async function sendEcho() {
            const message = document.getElementById('messageInput').value;
            try {
                const response = await fetch('/api/echo', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: message})
                });
                const data = await response.json();
                document.getElementById('httpOutput').innerHTML = 
                    `<strong>Echo Response:</strong><br>Message: ${data.message}<br>Timestamp: ${data.timestamp}`;
            } catch (error) {
                document.getElementById('httpOutput').innerHTML = `<strong>Error:</strong> ${error.message}`;
            }
        }

        // Get Server Status
        async function getStatus() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                document.getElementById('httpOutput').innerHTML = 
                    `<strong>Server Status:</strong><br>Uptime: ${data.uptime.toFixed(1)} seconds<br>Requests Handled: ${data.requests_handled}`;
            } catch (error) {
                document.getElementById('httpOutput').innerHTML = `<strong>Error:</strong> ${error.message}`;
            }
        }

        // WebSocket Connection
        function connectSocket() {
            if (isConnected) return;
            
            socket = io();
            
            socket.on('connect', () => {
                isConnected = true;
                document.getElementById('connectBtn').disabled = true;
                document.getElementById('disconnectBtn').disabled = false;
                addRealtimeMessage('✅ Connected to server');
            });
            
            socket.on('disconnect', () => {
                isConnected = false;
                document.getElementById('connectBtn').disabled = false;
                document.getElementById('disconnectBtn').disabled = true;
                addRealtimeMessage('❌ Disconnected from server');
            });
            
            socket.on('server_broadcast', (data) => {
                addRealtimeMessage(`📢 Server: ${data.message} (${data.timestamp})`);
            });
            
            socket.on('message_response', (data) => {
                addRealtimeMessage(`💬 Echo: ${data.message} (${data.timestamp})`);
            });
        }

        function disconnectSocket() {
            if (socket && isConnected) {
                socket.disconnect();
            }
        }

        function sendRealtimeMessage() {
            if (!isConnected) {
                alert('Please connect to WebSocket first');
                return;
            }
            const message = document.getElementById('realtimeInput').value;
            if (message.trim()) {
                socket.emit('client_message', {message: message});
                document.getElementById('realtimeInput').value = '';
                addRealtimeMessage(`📤 You: ${message}`);
            }
        }

        function addRealtimeMessage(message) {
            const output = document.getElementById('realtimeOutput');
            const div = document.createElement('div');
            div.innerHTML = `${new Date().toLocaleTimeString()} - ${message}`;
            output.appendChild(div);
            output.scrollTop = output.scrollHeight;
        }

        // Auto-connect on page load
        window.onload = () => {
            connectSocket();
        };
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    """Serve the client interface"""
    return render_template_string(CLIENT_HTML)

@app.route('/api/echo', methods=['POST'])
def echo():
    """Echo endpoint - returns the message with timestamp"""
    server_stats['requests_handled'] += 1
    
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'Message field required'}), 400
    
    response = {
        'message': data['message'],
        'timestamp': datetime.now().isoformat()
    }
    return jsonify(response)

@app.route('/api/status')
def status():
    """Server status endpoint"""
    server_stats['requests_handled'] += 1
    
    uptime = time.time() - server_stats['start_time']
    return jsonify({
        'uptime': uptime,
        'requests_handled': server_stats['requests_handled']
    })

# WebSocket Events (only if SocketIO is available)
if SOCKETIO_AVAILABLE:
    @socketio.on('connect')
    def handle_connect():
        print(f'Client connected: {request.sid}')
        emit('server_broadcast', {
            'message': 'Welcome to the network application!',
            'timestamp': datetime.now().isoformat()
        })

    @socketio.on('disconnect')
    def handle_disconnect():
        print(f'Client disconnected: {request.sid}')

    @socketio.on('client_message')
    def handle_client_message(data):
        """Handle realtime messages from clients"""
        print(f'Received message: {data}')
        # Echo the message back to the sender
        emit('message_response', {
            'message': data['message'],
            'timestamp': datetime.now().isoformat()
        })

    def broadcast_periodic_messages():
        """Send periodic broadcast messages to all connected clients"""
        import time
        while True:
            time.sleep(10)  # Send every 10 seconds
            if socketio:
                socketio.emit('server_broadcast', {
                    'message': f'Periodic broadcast - Server uptime: {time.time() - server_stats["start_time"]:.1f}s',
                    'timestamp': datetime.now().isoformat()
                })

if __name__ == '__main__':
    print("🚀 Starting Network Application Demo Server...")
    print("📍 Server will be available at: http://localhost:3000")
    print("💡 Open your browser to see the client interface")
    
    if SOCKETIO_AVAILABLE:
        # Start the periodic broadcast thread
        import threading
        broadcast_thread = threading.Thread(target=broadcast_periodic_messages, daemon=True)
        broadcast_thread.start()
        print("✅ WebSocket support enabled")
        socketio.run(app, host='0.0.0.0', port=3000, debug=True)
    else:
        print("⚠️  Running without WebSocket support")
        app.run(host='0.0.0.0', port=3000, debug=True)