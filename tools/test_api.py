# test_api.py - Save this in your root folder
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def wait_for_server(timeout=30):
    """Wait for server to start"""
    print("Waiting for server to start...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print("✅ Server is running!")
                return True
        except:
            print(".", end="", flush=True)
            time.sleep(2)
    
    print("\n❌ Server did not start in time")
    return False

def test_all_endpoints():
    print("🧪 Testing Agentic AI Chatbot API...")
    print("=" * 60)
    
    if not wait_for_server():
        print("Please start the server first with: python main.py")
        return
    
    tests = [
        ("Health Check", "GET", "/health", None),
        ("Root Endpoint", "GET", "/", None),
        ("Weather API", "GET", "/api/weather/London", None),
        ("Chat API", "POST", "/api/chat", {"message": "What is the weather in Chennai today?"}),
        ("Meetings API", "GET", "/api/meetings", None),
        ("Database Query", "GET", "/api/query?query=show meetings today", None),
    ]
    
    results = []
    
    for test_name, method, endpoint, data in tests:
        print(f"\n📡 Testing {test_name}...")
        print(f"   {method} {endpoint}")
        
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            elif method == "POST":
                response = requests.post(f"{BASE_URL}{endpoint}", json=data, timeout=10)
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Success")
                
                # Show brief result
                if isinstance(result, dict):
                    if "status" in result:
                        print(f"   Status: {result['status']}")
                    if "count" in result:
                        print(f"   Count: {result['count']}")
                    if "response" in result:
                        print(f"   Response: {result['response'][:100]}...")
                results.append((test_name, True))
            else:
                print(f"   ❌ Failed: {response.text[:100]}")
                results.append((test_name, False))
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS:")
    print("=" * 60)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if success:
            passed += 1
    
    total = len(results)
    print(f"\n📈 Score: {passed}/{total} passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Your Agentic AI Chatbot is working!")
    else:
        print(f"\n⚠ {total - passed} test(s) failed")
    
    return passed == total

def quick_test():
    """Quick test without waiting for server"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running!")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            print(f"❌ Server returned status: {response.status_code}")
            return False
    except:
        print("❌ Server not running. Start it with: python main.py")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        quick_test()
    else:
        test_all_endpoints()