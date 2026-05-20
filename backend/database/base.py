# database/base.py
from abc import ABC, abstractmethod
from typing import List, Optional
from database.models import (
    ChatModel,
    MessageModel,
    UpdateChatRequest
)

# ─────────────────────────────────────────────────
# Abstract Database Interface
# ─────────────────────────────────────────────────
class DatabaseRepository(ABC):
    """
    Abstract base class for all database implementations
    All methods now support user_id filtering!
    """
    
    # ── Connection Methods ────────────────────────
    @abstractmethod
    async def connect(self) -> None:
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        pass
    
    # ── CRUD Operations ───────────────────────────
    @abstractmethod
    async def create_chat(
        self, 
        chat: ChatModel
    ) -> ChatModel:
        pass
    
    @abstractmethod
    async def get_user_chats(
        self,
        user_id: str
    ) -> List[ChatModel]:
        """Get all chats for specific user"""
        pass
    
    @abstractmethod
    async def get_chat(
        self,
        chat_id: str,
        user_id: str
    ) -> Optional[ChatModel]:
        """Get chat - must belong to user"""
        pass
    
    @abstractmethod
    async def update_chat(
        self,
        chat_id: str,
        user_id: str,
        update : UpdateChatRequest
    ) -> Optional[ChatModel]:
        pass
    
    @abstractmethod
    async def add_message_to_chat(
        self,
        chat_id: str,
        user_id: str,
        message: MessageModel
    ) -> Optional[ChatModel]:
        pass
    
    @abstractmethod
    async def delete_chat(
        self,
        chat_id: str,
        user_id: str
    ) -> bool:
        pass
    
    @abstractmethod
    async def delete_all_user_chats(
        self,
        user_id: str
    ) -> int:
        """Delete all chats for specific user"""
        pass

