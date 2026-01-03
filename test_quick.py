# test_quick.py - Quick test to verify server is running
import requests
import time
import sys

def test_server():
    print("🧪 Testing Agentic AI Chatbot Server...")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Wait for server to start (max 30 seconds)
    print("Waiting for server to start...")
    for i in range(15):
        try:
            response = requests.get(f"{base_url}/health", timeout=2)
            if response.status_code == 200:
                print(f"✅ Server is running! (Attempt {i+1}/15)")
                break
        except:
            if i < 14:
                print(".", end="", flush=True)
                time.sleep(2)
            else:
                print("\n❌ Server didn't start in time")
                print("Please run: python main.py")
                return False
    
    print("\n📋 Testing endpoints:")
    
    endpoints = [
        ("GET", "/", "Root endpoint"),
        ("GET", "/health", "Health check"),
        ("GET", "/api/weather/London", "Weather API"),
        ("POST", "/api/chat", "Chat API"),
    ]
    
    for method, endpoint, description in endpoints:
        print(f"\n{description}...")
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
            else:  # POST
                data = {"message": "Hello from test!"}
                response = requests.post(f"{base_url}{endpoint}", json=data, timeout=5)
            
            if response.status_code == 200:
                print(f"   ✅ {method} {endpoint} - Status: {response.status_code}")
                result = response.json()
                if isinstance(result, dict):
                    if "status" in result:
                        print(f"   Status: {result['status']}")
                    if "response" in result:
                        print(f"   Response: {result['response'][:50]}...")
            else:
                print(f"   ❌ {method} {endpoint} - Status: {response.status_code}")
                print(f"   Error: {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("✅ Testing complete!")
    print("=" * 50)
    print("\n💡 Open your browser to:")
    print("   http://localhost:8000")
    print("   http://localhost:8000/docs")
    
    return True

if __name__ == "__main__":
    test_server()