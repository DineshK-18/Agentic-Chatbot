# init_database.py - Run this first
import os
import sys
from pathlib import Path

print("🗄️ Initializing Agentic AI Chatbot Database...")
print("=" * 60)

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Create necessary directories
directories = ["data", "uploads", "logs"]
for dir_name in directories:
    dir_path = project_root / dir_name
    dir_path.mkdir(exist_ok=True)
    print(f"✅ Created {dir_name}/ directory")

# Try to initialize database
try:
    from database.db import init_db
    init_db()
    
    print("\n" + "=" * 60)
    print("✅ DATABASE INITIALIZED SUCCESSFULLY!")
    print("=" * 60)
    
    # List database file
    db_path = project_root / "data" / "chatbot.db"
    if db_path.exists():
        print(f"📁 Database location: {db_path}")
        print(f"📊 File size: {db_path.stat().st_size} bytes")
    else:
        print("⚠ Database file not found")
        
    print("\n📋 Now you can run: python main.py")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\n💡 Try running as Administrator or in a different directory.")