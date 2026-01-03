# main.py - COMPLETE FIXED VERSION
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv(project_root / '.env')

from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
from datetime import datetime
import json
from sqlalchemy.orm import Session
from sqlalchemy import text  # SQLAlchemy 2.0 compatible

# Import agents
from agents.orchestrator import OrchestratorAgent
from tools.weather_tool import WeatherTool
from tools.document_tool import DocumentTool
from tools.database_tool import DatabaseTool
from database.db import get_db, init_db, SessionLocal

# Initialize database
print("🔧 Initializing database...")
init_db()

# Initialize tools
print("🤖 Initializing AI agents...")
weather_tool = WeatherTool()
document_tool = DocumentTool()
database_tool = DatabaseTool()

# Create orchestrator
orchestrator = OrchestratorAgent(
    weather_tool=weather_tool,
    document_tool=document_tool,
    database_tool=database_tool
)

# Create FastAPI app
app = FastAPI(
    title="Agentic AI Chatbot",
    description="Multi-agent AI system with weather, document, scheduling, and database capabilities",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Mount uploads directory for serving files
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Request models
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class WeatherRequest(BaseModel):
    location: str
    date: Optional[str] = None

class ScheduleRequest(BaseModel):
    location: str
    date: str
    title: Optional[str] = "Team Meeting"
    participants: Optional[List[str]] = []

# Root endpoint
@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Agentic AI Chatbot</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; }
            .endpoint { background: #f8f9fa; padding: 15px; margin: 10px 0; border-left: 4px solid #007bff; border-radius: 5px; }
            code { background: #e9ecef; padding: 2px 6px; border-radius: 3px; }
            .btn { display: inline-block; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 5px; }
            .btn:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Agentic AI Chatbot API</h1>
            <p>A multi-agent AI system with intelligent workflow orchestration</p>
            
            <h2>📡 Quick Links</h2>
            <p>
                <a href="/docs" class="btn">Interactive API Docs</a>
                <a href="/health" class="btn">Health Check</a>
                <a href="/api/endpoints" class="btn">All Endpoints</a>
            </p>
            
            <h2>🔧 Available Agents</h2>
            <ul>
                <li><strong>Weather Intelligence Agent</strong> - Real-time weather data</li>
                <li><strong>Document Understanding Agent</strong> - PDF/TXT analysis with web fallback</li>
                <li><strong>Meeting Scheduling Agent</strong> - Weather-aware scheduling</li>
                <li><strong>Database Query Agent</strong> - Natural language to SQL</li>
            </ul>
            
            <h2>🚀 Quick Test</h2>
            <div class="endpoint">
                <strong>POST /api/chat</strong><br>
                <code>curl -X POST http://localhost:8000/api/chat -H "Content-Type: application/json" -d '{"message": "What is the weather in London?"}'</code>
            </div>
            
            <p>For full documentation, visit <a href="/docs">/docs</a></p>
        </div>
    </html>
    """

# API Endpoints
@app.post("/api/chat")
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """Main chat endpoint - routes to appropriate agent"""
    try:
        response = orchestrator.process(
            message=request.message,
            conversation_id=request.conversation_id,
            db=db
        )
        return JSONResponse(content=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload document for analysis"""
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Validate file type
        allowed_extensions = {'.pdf', '.txt', '.docx'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"File type not allowed. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Save file
        file_path = f"uploads/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        os.makedirs("uploads", exist_ok=True)
        
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Process document
        result = document_tool.process_document(file_path, file.filename)
        
        return {
            "status": "success",
            "filename": file.filename,
            "file_path": file_path,
            "message": "Document uploaded and processed successfully",
            "document_info": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/api/weather/{location}")
async def get_weather_api(location: str, date: Optional[str] = None):
    """Direct weather API endpoint"""
    try:
        weather_data = weather_tool.get_weather(location, date)
        return weather_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/schedule")
async def schedule_meeting(request: ScheduleRequest, db: Session = Depends(get_db)):
    """Schedule a meeting with weather consideration"""
    try:
        result = orchestrator.schedule_meeting(
            location=request.location,
            date=request.date,
            title=request.title,
            participants=request.participants,
            db=db
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/meetings")
async def get_meetings(
    date: Optional[str] = None,
    location: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get meetings from database"""
    try:
        meetings = database_tool.get_meetings(db, date=date, location=location)
        return {
            "count": len(meetings),
            "meetings": meetings,
            "filters": {"date": date, "location": location}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/query")
async def query_database(
    query: str,
    db: Session = Depends(get_db)
):
    """Natural language database query"""
    try:
        result = database_tool.natural_language_query(query, db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint - SQLAlchemy 2.0 compatible"""
    try:
        # Test database connection
        db = SessionLocal()
        db.execute(text("SELECT 1"))  # text() wrapper for SQLAlchemy 2.0
        db.close()
        
        # Test weather service
        weather_status = "ready"
        if hasattr(weather_tool, 'check_status'):
            weather_status = weather_tool.check_status()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.0",
            "services": {
                "database": "connected",
                "weather_api": weather_status,
                "document_processor": "ready",
                "orchestrator": "ready"
            },
            "agents": ["weather", "document", "scheduling", "database"]
        }
    except Exception as e:
        # Don't fail, just report issue
        return {
            "status": "degraded",
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.0",
            "error": str(e),
            "note": "Some services may not be available"
        }

@app.get("/api/endpoints")
async def list_endpoints():
    """List all available API endpoints"""
    routes = []
    for route in app.routes:
        if hasattr(route, "methods"):
            routes.append({
                "path": route.path,
                "methods": list(route.methods),
                "name": route.name if hasattr(route, "name") else None
            })
    return {"endpoints": routes}

# Error handlers
@app.exception_handler(404)
async def not_found_exception_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Endpoint not found", "path": request.url.path}
    )

@app.exception_handler(500)
async def internal_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

def main():
    """Main function to run the application"""
    print("=" * 60)
    print("🤖 AGENTIC AI CHATBOT - Version 2.0.0")
    print("=" * 60)
    print("📡 Server starting on: http://localhost:8000")
    print("📖 Interactive docs: http://localhost:8000/docs")
    print("❤️  Health check: http://localhost:8000/health")
    print("=" * 60)
    
    # Run uvicorn server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()