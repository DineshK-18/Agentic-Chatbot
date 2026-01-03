# app/database/init_db.py
import os
from sqlalchemy import create_engine, text
from app.database.models import Base

def init_database():
    # Get database URL from environment variable
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/agentic_chatbot")
    
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    # Option 1: Create tables from SQLAlchemy models (recommended)
    print("Creating database tables from SQLAlchemy models...")
    Base.metadata.create_all(bind=engine)
    
    # Option 2: Execute raw SQL file
    # with open("app/database/schema.sql", "r") as f:
    #     sql_commands = f.read()
    #     with engine.connect() as connection:
    #         connection.execute(text(sql_commands))
    #         connection.commit()
    
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_database()