# database/models.py
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# ─────────────────────────────────────────────────
# Message Model
# ─────────────────────────────────────────────────
class MessageModel(BaseModel):
    """
    Single message in a chat
    """
    id        : str
    role      : str
    content   : str
    user_level: Optional[str] = None
    timestamp : datetime      = Field(
        default_factory=datetime.utcnow
    )

# ─────────────────────────────────────────────────
# Chat Model (with user_id!)
# ─────────────────────────────────────────────────
class ChatModel(BaseModel):
    """
    Complete chat with messages
    Now includes user_id for ownership!
    """
    id        : str
    user_id   : Optional[str] = None          # ← NEW!
    title     : str
    messages  : List[MessageModel] = []
    created_at: datetime           = Field(
        default_factory=datetime.utcnow
    )
    updated_at: datetime           = Field(
        default_factory=datetime.utcnow
    )

# ─────────────────────────────────────────────────
# Request Models
# ─────────────────────────────────────────────────
class CreateChatRequest(BaseModel):
    title: str = "New Chat"

class UpdateChatRequest(BaseModel):
    title   : Optional[str]                = None
    messages: Optional[List[MessageModel]] = None

class AddMessageRequest(BaseModel):
    message: MessageModel

