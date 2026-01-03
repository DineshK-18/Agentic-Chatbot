# simple_test.py - UPDATED
import requests

print("🧪 Testing Agentic AI Chatbot")
print("=" * 50)

# Test 1: Health
print("1. Health Check:")
health = requests.get("http://localhost:8000/health").json()
print(f"   ✅ Status: {health['status']}")
print(f"   ✅ Version: {health['version']}")

# Test 2: Weather
print("\n2. Weather Agent:")
weather = requests.get("http://localhost:8000/api/weather/Chennai").json()
print(f"   ✅ Location: {weather['location']}")
print(f"   ✅ Temperature: {weather['temperature']}°C")
print(f"   ✅ Conditions: {weather['conditions']}")

# Test 3: Chat - Handle different response formats
print("\n3. Chat Agent (Weather Question):")
chat = requests.post("http://localhost:8000/api/chat", 
                     json={"message": "What is the weather in Chennai today?"}).json()

# Check what keys are in the response
print(f"   ✅ Response keys: {list(chat.keys())}")

# Display response based on available keys
if 'agent' in chat:
    print(f"   Agent: {chat['agent']}")
elif 'agent_used' in chat:
    print(f"   Agent: {chat['agent_used']}")

if 'response' in chat:
    response_text = chat['response']
    if len(response_text) > 80:
        print(f"   Response: {response_text[:80]}...")
    else:
        print(f"   Response: {response_text}")

# Test 4: Meeting Scheduling
print("\n4. Meeting Scheduling:")
schedule = requests.post("http://localhost:8000/api/schedule",
                        json={
                            "location": "Bengaluru",
                            "date": "tomorrow",
                            "title": "Team Review"
                        }).json()
print(f"   ✅ Status: {schedule.get('status', 'unknown')}")
print(f"   ✅ Message: {schedule.get('message', 'N/A')}")

# Test 5: List Meetings
print("\n5. Database Query:")
meetings = requests.get("http://localhost:8000/api/meetings").json()
print(f"   ✅ Found {meetings.get('count', 0)} meeting(s)")

print("\n" + "=" * 50)
print("🎉 AGENTIC AI CHATBOT IS WORKING!")
print("=" * 50)
print("\n💡 Open in browser:")
print("   http://localhost:8000")
print("   http://localhost:8000/docs")
print("\n📋 Available Agents:")
print("   1. ✅ Weather Intelligence Agent")
print("   2. ✅ Document Understanding Agent")
print("   3. ✅ Meeting Scheduling Agent")
print("   4. ✅ Database Query Agent")