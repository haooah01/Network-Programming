import requests
import socketio
import time
import threading
import sys

class NetworkClientDemo:
    """
    Standalone Python client to test the network application
    Demonstrates both HTTP and WebSocket communication
    """
    
    def __init__(self, server_url='http://localhost:3000'):
        self.server_url = server_url
        self.sio = socketio.Client()
        self.connected = False
        self.setup_socketio_handlers()
    
    def setup_socketio_handlers(self):
        """Setup WebSocket event handlers"""
        @self.sio.event
        def connect():
            print("✅ WebSocket connected to server")
            self.connected = True
        
        @self.sio.event
        def disconnect():
            print("❌ WebSocket disconnected from server")
            self.connected = False
        
        @self.sio.on('server_broadcast')
        def on_server_broadcast(data):
            print(f"📢 Server broadcast: {data['message']} ({data['timestamp']})")
        
        @self.sio.on('message_response')
        def on_message_response(data):
            print(f"💬 Message echo: {data['message']} ({data['timestamp']})")
    
    def test_http_echo(self, message="Hello from Python client!"):
        """Test the HTTP echo endpoint"""
        try:
            print(f"\n📡 Testing HTTP Echo with message: '{message}'")
            response = requests.post(
                f"{self.server_url}/api/echo",
                json={'message': message},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Echo successful: {data['message']} (timestamp: {data['timestamp']})")
                return True
            else:
                print(f"❌ Echo failed with status {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ HTTP request failed: {e}")
            return False
    
    def test_http_status(self):
        """Test the HTTP status endpoint"""
        try:
            print(f"\n📊 Testing Server Status")
            response = requests.get(f"{self.server_url}/api/status", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Server uptime: {data['uptime']:.1f} seconds")
                print(f"✅ Requests handled: {data['requests_handled']}")
                return True
            else:
                print(f"❌ Status request failed with status {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Status request failed: {e}")
            return False
    
    def connect_websocket(self):
        """Connect to WebSocket"""
        try:
            print(f"\n🔌 Connecting to WebSocket at {self.server_url}")
            self.sio.connect(self.server_url)
            time.sleep(1)  # Give it a moment to connect
            return self.connected
        except Exception as e:
            print(f"❌ WebSocket connection failed: {e}")
            return False
    
    def send_websocket_message(self, message="Hello via WebSocket!"):
        """Send a message via WebSocket"""
        if not self.connected:
            print("❌ WebSocket not connected")
            return False
        
        try:
            print(f"📤 Sending WebSocket message: '{message}'")
            self.sio.emit('client_message', {'message': message})
            return True
        except Exception as e:
            print(f"❌ Failed to send WebSocket message: {e}")
            return False
    
    def run_comprehensive_test(self):
        """Run a comprehensive test of all features"""
        print("🚀 Starting Network Application Client Test")
        print("=" * 50)
        
        # Test HTTP endpoints
        http_echo_success = self.test_http_echo()
        http_status_success = self.test_http_status()
        
        # Test WebSocket
        ws_connect_success = self.connect_websocket()
        ws_message_success = False
        
        if ws_connect_success:
            ws_message_success = self.send_websocket_message()
            
            # Wait a bit to receive some broadcast messages
            print("\n⏳ Waiting 15 seconds to receive broadcast messages...")
            time.sleep(15)
            
            # Send another message
            self.send_websocket_message("Test message 2")
            time.sleep(2)
        
        # Disconnect
        if self.connected:
            print("\n🔌 Disconnecting WebSocket...")
            self.sio.disconnect()
        
        # Summary
        print("\n" + "=" * 50)
        print("📋 Test Results Summary:")
        print(f"HTTP Echo: {'✅ PASS' if http_echo_success else '❌ FAIL'}")
        print(f"HTTP Status: {'✅ PASS' if http_status_success else '❌ FAIL'}")
        print(f"WebSocket Connect: {'✅ PASS' if ws_connect_success else '❌ FAIL'}")
        print(f"WebSocket Message: {'✅ PASS' if ws_message_success else '❌ FAIL'}")
        
        all_passed = all([http_echo_success, http_status_success, ws_connect_success, ws_message_success])
        print(f"\nOverall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
        
        return all_passed

def main():
    """Main function to run the client demo"""
    if len(sys.argv) > 1:
        server_url = sys.argv[1]
    else:
        server_url = 'http://localhost:3000'
    
    print(f"Network Client Demo - Connecting to {server_url}")
    
    client = NetworkClientDemo(server_url)
    client.run_comprehensive_test()

if __name__ == '__main__':
    main()