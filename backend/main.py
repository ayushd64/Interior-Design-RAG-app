# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from api.routes import router as api_router
from api.chat_routes import router as chat_router
from database.connection import (
    connect_to_mongo,
    close_mongo_connection
)
from src.vector_db.factory import (
    init_vector_db,
    close_vector_db
)
from dotenv import load_dotenv
import os

load_dotenv()

# ── Lifespan Manager ──────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n" + "="*50)
    print("Starting Interior Design RAG API...")
    print("="*50)
    
    # Connect to vector database
    await init_vector_db()
    
    # Connect to chat database
    await connect_to_mongo()
    
    yield
    
    print("\nShutting down...")
    await close_mongo_connection()
    await close_vector_db()

# ── Initialize FastAPI App ────────────────────────
app = FastAPI(
    title       = "Interior Design RAG API",
    description = "AI powered interior design assistant",
    version     = "1.0.0",
    lifespan    = lifespan
)

# ── CORS Middleware ───────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins     = [
        os.getenv("FRONTEND_URL", "http://localhost:3000")
    ],
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"]
)

# ── Include Routes ────────────────────────────────
app.include_router(api_router, prefix="/api")
app.include_router(chat_router, prefix="/api")

# ── Root Endpoint ─────────────────────────────────
@app.get("/")
async def root():
    return {
        "message": "Welcome to the Interior Design RAG API! Visit /docs for API documentation.",
        "docs"   : "http://localhost:8000/docs",
        "status" : "running"
    }

# ── Run App ───────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("API_PORT", 8000))
    host = os.getenv("API_HOST", "0.0.0.0")
    
    print("\n" + "="*50)
    print("🚀 Interior Design RAG API is starting...")
    print("="*50)
    print(f"📡 API URL    : http://localhost:{port}")
    print(f"📚 API Docs   : http://localhost:{port}/docs")
    print(f"❤️  Health    : http://localhost:{port}/api/health")
    print("="*50 + "\n")
    
    uvicorn.run(
        "main:app",
        host   = host,
        port   = port,
        reload = True
    )

