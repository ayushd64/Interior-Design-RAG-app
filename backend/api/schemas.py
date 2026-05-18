# api/schemas.py
from pydantic import BaseModel
from typing import Optional, List

# ── Chat History Message ──────────────────────────
class HistoryMessage(BaseModel):
    """
    Single message in chat history
    """
    role   : str  # "user" or "assistant"
    content: str

# ── Request Models ────────────────────────────────
class ChatRequest(BaseModel):
    """
    Request model for chat endpoint
    Now includes chat history!
    """
    question    : str
    chat_history: Optional[List[HistoryMessage]] = []

    class Config:
        json_schema_extra = {
            "example": {
                "question"    : "What colors should I use?",
                "chat_history": [
                    {
                        "role"   : "user",
                        "content": "I have a small bedroom"
                    },
                    {
                        "role"   : "assistant",
                        "content": "For small bedrooms..."
                    }
                ]
            }
        }

class IngestRequest(BaseModel):
    confirm: bool = True

# ── Response Models ───────────────────────────────
class ChatResponse(BaseModel):
    question   : str
    answer     : str
    user_level : str
    success    : bool

class IngestResponse(BaseModel):
    success: bool
    message: str
    chunks : Optional[int] = None

class HealthResponse(BaseModel):
    status : str
    message: str