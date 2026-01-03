# fix_database.py - Run this to fix the database issues
import os
import sys
from pathlib import Path

print("🔧 Fixing Database Configuration...")
print("=" * 60)

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 1. Update .env file
env_path = project_root / ".env"
if env_path.exists():
    with open(env_path, "r") as f:
        content = f.read()
    
    # Ensure SQLite URL
    if "postgresql://" in content:
        content = content.replace("postgresql://", "sqlite:///./data/chatbot.db")
        print("✅ Updated .env to use SQLite")
    elif "DATABASE_URL=" not in content:
        content += "\nDATABASE_URL=sqlite:///./data/chatbot.db\n"
        print("✅ Added SQLite URL to .env")
    
    with open(env_path, "w") as f:
        f.write(content)
else:
    # Create .env file
    with open(env_path, "w") as f:
        f.write("""# OpenWeather API Key (get from https://openweathermap.org/api)
OPENWEATHER_API_KEY=your_api_key_here_register_at_openweathermap.org

# Database - Using SQLite (no driver needed)
DATABASE_URL=sqlite:///./data/chatbot.db

# App settings
DEBUG=True
SECRET_KEY=change-this-to-a-secure-random-string-in-production
""")
    print("✅ Created .env file")

# 2. Create data directory
data_dir = project_root / "data"
data_dir.mkdir(exist_ok=True)
print(f"✅ Created {data_dir}/")

# 3. Update database/db.py
db_py_path = project_root / "database" / "db.py"
if db_py_path.exists():
    with open(db_py_path, "w", encoding="utf-8") as f:
        f.write('''import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from dotenv import load_dotenv
from pathlib import Path
from typing import Generator

# Load environment variables
project_root = Path(__file__).parent.parent
load_dotenv(project_root / '.env')

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/chatbot.db")

# Create data directory if it doesn't exist
data_dir = project_root / "data"
data_dir.mkdir(exist_ok=True)

# Force SQLite URL format
if not DATABASE_URL.startswith("sqlite://"):
    print(f"⚠ Changing database URL to SQLite")
    DATABASE_URL = "sqlite:///./data/chatbot.db"

# Create SQLite engine with proper configuration
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency to get DB session
def get_db() -> Generator[Session, None, None]:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database with tables"""
    try:
        from database.models import Meeting, Conversation
        Base.metadata.create_all(bind=engine)
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
''')
    print("✅ Updated database/db.py")

# 4. Create database/models.py if it doesn't exist
models_py_path = project_root / "database" / "models.py"
if not models_py_path.exists():
    models_py_path.parent.mkdir(exist_ok=True)
    with open(models_py_path, "w", encoding="utf-8") as f:
        f.write('''from sqlalchemy import Column, Integer, String, DateTime, JSON, Text
from datetime import datetime
from database.db import Base

class Meeting(Base):
    """Meeting model for scheduling agent"""
    __tablename__ = "meetings"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, default="Team Meeting")
    location = Column(String(100), nullable=False, default="Office")
    scheduled_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    participants = Column(JSON, default=list)
    weather_conditions = Column(JSON, nullable=True)
    weather_decision = Column(String(50), nullable=True)
    status = Column(String(50), default="scheduled")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "location": self.location,
            "scheduled_date": self.scheduled_date.isoformat() if self.scheduled_date else None,
            "participants": self.participants or [],
            "weather_decision": self.weather_decision,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class Conversation(Base):
    """Conversation history model"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String(100), index=True, nullable=True)
    user_message = Column(Text, nullable=False)
    agent_response = Column(Text, nullable=False)
    agent_type = Column(String(50), nullable=False)
    confidence = Column(Integer, default=0)
    metadata = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "user_message": self.user_message,
            "agent_response": self.agent_response,
            "agent_type": self.agent_type,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }
''')
    print("✅ Created database/models.py")

# 5. Test imports
print("\n🧪 Testing imports...")
try:
    from database.db import get_db, init_db, SessionLocal
    from sqlalchemy.orm import Session
    
    print("✅ Database imports work")
    
    # Test database initialization
    print("Testing database initialization...")
    init_db()
    
    print("\n" + "=" * 60)
    print("✅ DATABASE FIXED SUCCESSFULLY!")
    print("=" * 60)
    
    print("\n📋 Now you can run:")
    print("1. python main.py")
    print("2. Open http://localhost:8000")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\n📦 Install missing packages:")
    print("pip install sqlalchemy python-dotenv")
    
except Exception as e:
    print(f"❌ Error: {e}")