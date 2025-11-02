import pytest
import json
from server import app, server_stats
import time

@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_route(client):
    """Test that the index route serves the HTML client"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Network Application Demo' in response.data

def test_echo_endpoint_success(client):
    """Test the echo endpoint with valid data"""
    test_message = "Hello, Network!"
    response = client.post('/api/echo', 
                          data=json.dumps({'message': test_message}),
                          content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == test_message
    assert 'timestamp' in data

def test_echo_endpoint_missing_message(client):
    """Test the echo endpoint with missing message field"""
    response = client.post('/api/echo', 
                          data=json.dumps({}),
                          content_type='application/json')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_status_endpoint(client):
    """Test the status endpoint"""
    response = client.get('/api/status')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'uptime' in data
    assert 'requests_handled' in data
    assert isinstance(data['uptime'], (int, float))
    assert isinstance(data['requests_handled'], int)

def test_multiple_requests_increment_counter(client):
    """Test that multiple requests increment the request counter"""
    # Get initial count
    response1 = client.get('/api/status')
    initial_count = json.loads(response1.data)['requests_handled']
    
    # Make an echo request
    client.post('/api/echo', 
                data=json.dumps({'message': 'test'}),
                content_type='application/json')
    
    # Check count increased
    response2 = client.get('/api/status')
    final_count = json.loads(response2.data)['requests_handled']
    
    assert final_count > initial_count