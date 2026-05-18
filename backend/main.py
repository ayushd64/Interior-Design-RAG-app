from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from dotenv import load_dotenv
import os

load_dotenv()

# ── Initialize FastAPI App ────────────────────────
app = FastAPI(
    title       = "Interior Design RAG API",
    description = "AI powered interior design assistant",
    version     = "1.0.0"
)

# ── CORS Middleware ───────────────────────────────
# Allows frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ── Include Routes ────────────────────────────────
app.include_router(router, prefix="/api")

# ── Root Endpoint ─────────────────────────────────
@app.get("/")
async def root():
    return {
        "message": "Welcome to the Interior Design RAG API! Visit /docs for API documentation.",
        "docs": "http://localhost:8000/docs",
        "status": "running"
        }

# ── Run App ───────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("API_PORT", 8000))
    host = os.getenv("API_HOST", "0.0.0.0")
    
    # ── Print Clickable URLs ──────────────────────
    print("\n" + "="*50)
    print("🚀 Interior Design RAG API is starting...")
    print("="*50)
    print(f"📡 API URL    : http://localhost:{port}")
    print(f"📚 API Docs   : http://localhost:{port}/docs")
    print(f"❤️  Health    : http://localhost:{port}/api/health")
    print("="*50 + "\n")
    
    uvicorn.run(
        "main:app",
        host    = host,
        port    = port,
        reload  = True
    )