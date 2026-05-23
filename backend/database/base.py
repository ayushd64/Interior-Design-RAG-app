# database/base.py
from abc import ABC, abstractmethod
from typing import List, Optional
from database.metrics_models import MetricLog
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

    # ── Metrics Operations ────────────────────────
    @abstractmethod
    async def log_metric(
        self,
        metric: "MetricLog"
    ) -> None:
        """Log a metric entry"""
        pass
    
    @abstractmethod
    async def get_metrics(
        self,
        user_id: str,
        limit  : int = 100
    ) -> List["MetricLog"]:
        """Get recent metrics for user"""
        pass
    
    @abstractmethod
    async def get_metric(
        self,
        metric_id: str,
        user_id  : str
    ) -> Optional["MetricLog"]:
        """Get single metric by ID"""
        pass
    
    @abstractmethod
    async def update_metric_rating(
        self,
        metric_id: str,
        user_id  : str,
        rating   : int
    ) -> bool:
        """Update user rating for a metric"""
        pass

    @abstractmethod
    async def update_metric_scores(
        self,
        metric_id: str,
        scores   : dict
    ) -> bool:
        """Update RAGAS scores for a metric"""
        pass




