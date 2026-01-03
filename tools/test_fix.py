# test_fix.py - Save this in your root folder (same as main.py)
import sys
import os
from pathlib import Path

print("🧪 Testing Agentic AI Chatbot Setup...")
print("=" * 60)

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    print("1. Testing Python environment...")
    print(f"   Python version: {sys.version}")
    print(f"   Current directory: {project_root}")
    
    print("\n2. Testing database imports...")
    from database.db import SessionLocal, get_db
    from sqlalchemy.orm import Session
    print("   ✅ Database imports work correctly")
    
    print("\n3. Testing type annotations...")
    def test_function(db: Session):
        return "Session type works"
    
    test_result = test_function(SessionLocal())
    print(f"   ✅ Type annotations work: {test_result}")
    
    print("\n4. Testing FastAPI imports...")
    from fastapi import Depends, FastAPI
    print("   ✅ FastAPI imports work correctly")
    
    print("\n5. Testing agent imports...")
    from agents.orchestrator import OrchestratorAgent
    from tools.weather_tool import WeatherTool
    from tools.document_tool import DocumentTool
    from tools.database_tool import DatabaseTool
    print("   ✅ All agent imports work")
    
    print("\n6. Testing environment variables...")
    from dotenv import load_dotenv
    load_dotenv(project_root / '.env')
    
    openweather_key = os.getenv("OPENWEATHER_API_KEY")
    if openweather_key and openweather_key != "your_api_key_here_register_at_openweathermap.org":
        print("   ✅ OpenWeather API key is set")
    else:
        print("   ⚠ OpenWeather API key not set (will use mock data)")
    
    db_url = os.getenv("DATABASE_URL", "sqlite:///./data/chatbot.db")
    print(f"   Database URL: {db_url}")
    
    print("\n7. Creating required directories...")
    directories = ["data", "uploads", "logs"]
    for dir_name in directories:
        dir_path = project_root / dir_name
        dir_path.mkdir(exist_ok=True)
        print(f"   ✅ {dir_name}/ directory ready")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    
    print("\n📋 NEXT STEPS:")
    print("1. Get OpenWeather API key from: https://openweathermap.org/api")
    print("2. Update the .env file with your API key")
    print("3. Run the application: python main.py")
    print("4. Open browser: http://localhost:8000")
    
except ImportError as e:
    print(f"\n❌ IMPORT ERROR: {e}")
    print("\n📦 Installing required packages...")
    print("Run: pip install -r requirements.txt")
    
    # Try to install
    try:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "fastapi", "uvicorn", "sqlalchemy", "python-dotenv"])
        print("✅ Packages installed. Run test again.")
    except:
        print("⚠ Could not install automatically.")
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()