from flask import Flask, request, jsonify
import time
from datetime import datetime

app = Flask(__name__)

# Server statistics
server_stats = {
    'start_time': time.time(),
    'requests_handled': 0
}

# Simple HTML client
CLIENT_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Network Application Demo</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        .output { background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 3px; }
        button { padding: 8px 16px; margin: 5px; cursor: pointer; }
        input[type="text"] { padding: 8px; margin: 5px; width: 200px; }
    </style>
</head>
<body>
    <h1>🌐 Network Application Demo</h1>
    <p>This application demonstrates HTTP network communication between client and server devices.</p>
    
    <div class="section">
        <h2>📡 HTTP Request/Response</h2>
        <div>
            <input type="text" id="messageInput" placeholder="Enter message" value="Hello, Network!">
            <button onclick="sendEcho()">Send Echo Request</button>
            <button onclick="getStatus()">Get Server Status</button>
        </div>
        <div class="output" id="httpOutput">HTTP responses will appear here...</div>
    </div>

    <script>
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
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    """Serve the client interface"""
    return CLIENT_HTML

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

if __name__ == '__main__':
    print("🚀 Starting Simple Network Application Server...")
    print("📍 Server will be available at: http://localhost:3000")
    print("💡 Open your browser to see the client interface")
    
    app.run(host='0.0.0.0', port=3000, debug=True)