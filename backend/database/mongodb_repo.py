# database/mongodb_repo.py
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional
from datetime import datetime
from database.base import DatabaseRepository
from database.metrics_models import MetricLog
from database.models import (
    ChatModel,
    MessageModel,
    UpdateChatRequest
)
from dotenv import load_dotenv
import os

load_dotenv()

class MongoDBRepository(DatabaseRepository):
    """MongoDB implementation with user filtering"""
    
    def __init__(self):
        self.client     = None
        self.database   = None
        self.collection = None
        self.url        = os.getenv(
            "MONGODB_URL",
            "mongodb://127.0.0.1:27017"
        )
        self.db_name    = os.getenv(
            "MONGODB_DB_NAME",
            "interior_design_rag"
        )
        self.collection_name = "chats"
        self.metrics_collection_name = "metrics"
    
    # ── Connection ────────────────────────────────
    async def connect(self) -> None:
        print(f"🔍 Connecting to MongoDB: {self.url}")
        try:
            self.client     = AsyncIOMotorClient(
                self.url,
                serverSelectionTimeoutMS=5000
            )
            self.database   = self.client[self.db_name]
            self.collection = self.database[self.collection_name]
            self.metrics_collection = self.database[self.metrics_collection_name]
            await self.client.admin.command('ping')
            print("✅ MongoDB connected successfully!")
            print(f"   Database: {self.db_name}")
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            raise
    
    async def disconnect(self) -> None:
        if self.client:
            self.client.close()
            print("✅ MongoDB connection closed!")
    
    # ── CRUD With User Filtering ──────────────────
    async def create_chat(
        self, 
        chat: ChatModel
    ) -> ChatModel:
        chat_dict = chat.model_dump()
        await self.collection.insert_one(chat_dict)
        print(f"✅ Chat created: {chat.id} for user {chat.user_id}")
        return chat
    
    async def get_user_chats(
        self,
        user_id: str
    ) -> List[ChatModel]:
        """Get chats only for specific user"""
        cursor = self.collection.find(
            {"user_id": user_id}
        ).sort("updated_at", -1)
        
        chats = await cursor.to_list(length=None)
        return [ChatModel(**chat) for chat in chats]
    
    async def get_chat(
        self,
        chat_id: str,
        user_id: str
    ) -> Optional[ChatModel]:
        """Get chat only if it belongs to user"""
        chat = await self.collection.find_one({
            "id"     : chat_id,
            "user_id": user_id
        })
        
        if not chat:
            return None
        return ChatModel(**chat)
    
    async def update_chat(
        self,
        chat_id: str,
        user_id: str,
        update : UpdateChatRequest
    ) -> Optional[ChatModel]:
        update_dict = {}
        
        if update.title is not None:
            update_dict["title"] = update.title
        
        if update.messages is not None:
            update_dict["messages"] = [
                msg.model_dump() for msg in update.messages
            ]
        
        update_dict["updated_at"] = datetime.utcnow()
        
        result = await self.collection.update_one(
            {
                "id"     : chat_id,
                "user_id": user_id
            },
            {"$set": update_dict}
        )
        
        if result.modified_count == 0:
            return None
        return await self.get_chat(chat_id, user_id)
    
    async def add_message_to_chat(
        self,
        chat_id: str,
        user_id: str,
        message: MessageModel
    ) -> Optional[ChatModel]:
        result = await self.collection.update_one(
            {
                "id"     : chat_id,
                "user_id": user_id
            },
            {
                "$push": {"messages": message.model_dump()},
                "$set" : {"updated_at": datetime.utcnow()}
            }
        )
        
        if result.modified_count == 0:
            return None
        return await self.get_chat(chat_id, user_id)
    
    async def delete_chat(
        self,
        chat_id: str,
        user_id: str
    ) -> bool:
        result = await self.collection.delete_one({
            "id"     : chat_id,
            "user_id": user_id
        })
        return result.deleted_count > 0
    
    async def delete_all_user_chats(
        self,
        user_id: str
    ) -> int:
        result = await self.collection.delete_many({
            "user_id": user_id
        })
        return result.deleted_count
    
    # ── Metrics Operations ────────────────────────
    async def log_metric(
        self,
        metric: MetricLog
    ) -> None:
        """Log a metric entry"""
        await self.metrics_collection.insert_one(
            metric.model_dump()
        )
    
    async def get_metrics(
        self,
        user_id: str,
        limit  : int = 100
    ) -> List[MetricLog]:
        """Get recent metrics for user"""
        cursor = self.metrics_collection.find(
            {"user_id": user_id}
        ).sort("timestamp", -1).limit(limit)
        
        metrics = await cursor.to_list(length=limit)
        return [MetricLog(**m) for m in metrics]
    
    async def get_metric(
        self,
        metric_id: str,
        user_id  : str
    ) -> Optional[MetricLog]:
        """Get single metric by ID"""
        metric = await self.metrics_collection.find_one({
            "id"     : metric_id,
            "user_id": user_id
        })
        if not metric:
            return None
        return MetricLog(**metric)
    
    async def update_metric_rating(
        self,
        metric_id: str,
        user_id  : str,
        rating   : int
    ) -> bool:
        """Update user rating"""
        result = await self.metrics_collection.update_one(
            {"id": metric_id, "user_id": user_id},
            {"$set": {"user_rating": rating}}
        )
        return result.modified_count > 0

    async def update_metric_scores(
        self,
        metric_id: str,
        scores   : dict
    ) -> bool:
        """Update evaluation scores"""
        result = await self.metrics_collection.update_one(
            {"id": metric_id},
            {"$set": {
                "faithfulness"     : scores.get("faithfulness"),
                "answer_relevancy" : scores.get("answer_relevancy"),
                "context_precision": scores.get("context_precision")
            }}
        )
        return result.modified_count > 0


