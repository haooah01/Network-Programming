import requests
import time

class SimpleNetworkClient:
    """
    Simple Python client to test the network application
    Demonstrates HTTP communication
    """
    
    def __init__(self, server_url='http://localhost:3000'):
        self.server_url = server_url
    
    def test_http_echo(self, message="Hello from Python client!"):
        """Test the HTTP echo endpoint"""
        try:
            print(f"\nTesting HTTP Echo with message: '{message}'")
            response = requests.post(
                f"{self.server_url}/api/echo",
                json={'message': message},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"SUCCESS: Echo response: {data['message']} (timestamp: {data['timestamp']})")
                return True
            else:
                print(f"ERROR: Echo failed with status {response.status_code}")
                return False
        except Exception as e:
            print(f"ERROR: HTTP request failed: {e}")
            return False
    
    def test_http_status(self):
        """Test the HTTP status endpoint"""
        try:
            print(f"\nTesting Server Status")
            response = requests.get(f"{self.server_url}/api/status", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                print(f"SUCCESS: Server uptime: {data['uptime']:.1f} seconds")
                print(f"SUCCESS: Requests handled: {data['requests_handled']}")
                return True
            else:
                print(f"ERROR: Status request failed with status {response.status_code}")
                return False
        except Exception as e:
            print(f"ERROR: Status request failed: {e}")
            return False
    
    def run_test(self):
        """Run a comprehensive test"""
        print("Starting Network Application Client Test")
        print("=" * 50)
        
        # Test HTTP endpoints
        echo_success = self.test_http_echo()
        status_success = self.test_http_status()
        
        # Test with different messages
        echo2_success = self.test_http_echo("Second test message")
        
        # Check status again to see counter increment
        status2_success = self.test_http_status()
        
        # Summary
        print("\n" + "=" * 50)
        print("Test Results Summary:")
        print(f"HTTP Echo Test 1: {'PASS' if echo_success else 'FAIL'}")
        print(f"HTTP Status Test 1: {'PASS' if status_success else 'FAIL'}")
        print(f"HTTP Echo Test 2: {'PASS' if echo2_success else 'FAIL'}")
        print(f"HTTP Status Test 2: {'PASS' if status2_success else 'FAIL'}")
        
        all_passed = all([echo_success, status_success, echo2_success, status2_success])
        print(f"\nOverall: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
        
        return all_passed

if __name__ == '__main__':
    client = SimpleNetworkClient()
    client.run_test()