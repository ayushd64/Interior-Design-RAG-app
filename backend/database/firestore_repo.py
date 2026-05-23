# database/firestore_repo.py
import firebase_admin
from firebase_admin import credentials, firestore
from typing import List, Optional
from datetime import datetime
from database.metrics_models import MetricLog
from database.base import DatabaseRepository
from database.models import (
    ChatModel,
    MessageModel,
    UpdateChatRequest
)
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

class FirestoreRepository(DatabaseRepository):
    """Firestore implementation with user filtering"""
    
    def __init__(self):
        self.app             = None
        self.db              = None
        self.collection_name = os.getenv(
            "FIRESTORE_COLLECTION_NAME",
            "chats"
        )
        self.metrics_collection_name = "metrics"
        self.credentials_path = os.getenv(
            "FIREBASE_CREDENTIALS_PATH",
            "./firebase-credentials.json"
        )
    
    # ── Connection ────────────────────────────────
    async def connect(self) -> None:
        print(f"🔍 Connecting to Firestore...")
        print(f"   Credentials: {self.credentials_path}")
        
        try:
            if not os.path.exists(self.credentials_path):
                raise FileNotFoundError(
                    f"Firebase credentials not found at: "
                    f"{self.credentials_path}"
                )
            
            if not firebase_admin._apps:
                cred = credentials.Certificate(
                    self.credentials_path
                )
                self.app = firebase_admin.initialize_app(cred)
            else:
                self.app = firebase_admin.get_app()
            
            self.db = firestore.client()
            print("✅ Firestore connected successfully!")
            print(f"   Collection: {self.collection_name}")
        except Exception as e:
            print(f"❌ Firestore connection failed: {e}")
            raise
    
    async def disconnect(self) -> None:
        # Don't delete app since auth uses same!
        self.db  = None
    
    # ── Helpers ───────────────────────────────────
    def _doc_to_chat(self, doc_data: dict) -> ChatModel:
        if isinstance(doc_data.get("created_at"), str):
            doc_data["created_at"] = datetime.fromisoformat(
                doc_data["created_at"]
            )
        if isinstance(doc_data.get("updated_at"), str):
            doc_data["updated_at"] = datetime.fromisoformat(
                doc_data["updated_at"]
            )
        for msg in doc_data.get("messages", []):
            if isinstance(msg.get("timestamp"), str):
                msg["timestamp"] = datetime.fromisoformat(
                    msg["timestamp"]
                )
        return ChatModel(**doc_data)
    
    # ── CRUD With User Filtering ──────────────────
    async def create_chat(
        self, 
        chat: ChatModel
    ) -> ChatModel:
        doc_ref = self.db.collection(
            self.collection_name
        ).document(chat.id)
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: doc_ref.set(chat.model_dump())
        )
        
        print(f"✅ Chat created in Firestore: {chat.id}")
        return chat
    
    async def get_user_chats(
        self,
        user_id: str
    ) -> List[ChatModel]:
        loop = asyncio.get_event_loop()
        
        docs = await loop.run_in_executor(
            None,
            lambda: list(
                self.db.collection(self.collection_name)
                .where("user_id", "==", user_id)
                .order_by(
                    "updated_at",
                    direction=firestore.Query.DESCENDING
                )
                .stream()
            )
        )
        
        chats = []
        for doc in docs:
            try:
                data = doc.to_dict()
                chats.append(self._doc_to_chat(data))
            except Exception as e:
                print(f"⚠️ Error parsing chat {doc.id}: {e}")
                continue
        return chats
    
    async def get_chat(
        self,
        chat_id: str,
        user_id: str
    ) -> Optional[ChatModel]:
        loop = asyncio.get_event_loop()
        
        doc = await loop.run_in_executor(
            None,
            lambda: self.db.collection(
                self.collection_name
            ).document(chat_id).get()
        )
        
        if not doc.exists:
            return None
        
        data = doc.to_dict()
        # Verify user owns this chat!
        if data.get("user_id") != user_id:
            return None
        
        return self._doc_to_chat(data)
    
    async def update_chat(
        self,
        chat_id: str,
        user_id: str,
        update : UpdateChatRequest
    ) -> Optional[ChatModel]:
        existing = await self.get_chat(chat_id, user_id)
        if not existing:
            return None
        
        update_dict = {}
        if update.title is not None:
            update_dict["title"] = update.title
        if update.messages is not None:
            update_dict["messages"] = [
                msg.model_dump() for msg in update.messages
            ]
        update_dict["updated_at"] = datetime.utcnow()
        
        loop = asyncio.get_event_loop()
        doc_ref = self.db.collection(
            self.collection_name
        ).document(chat_id)
        
        await loop.run_in_executor(
            None,
            lambda: doc_ref.update(update_dict)
        )
        
        return await self.get_chat(chat_id, user_id)
    
    async def add_message_to_chat(
        self,
        chat_id: str,
        user_id: str,
        message: MessageModel
    ) -> Optional[ChatModel]:
        existing = await self.get_chat(chat_id, user_id)
        if not existing:
            return None
        
        loop = asyncio.get_event_loop()
        doc_ref = self.db.collection(
            self.collection_name
        ).document(chat_id)
        
        await loop.run_in_executor(
            None,
            lambda: doc_ref.update({
                "messages" : firestore.ArrayUnion([
                    message.model_dump()
                ]),
                "updated_at": datetime.utcnow()
            })
        )
        
        return await self.get_chat(chat_id, user_id)
    
    async def delete_chat(
        self,
        chat_id: str,
        user_id: str
    ) -> bool:
        existing = await self.get_chat(chat_id, user_id)
        if not existing:
            return False
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: self.db.collection(
                self.collection_name
            ).document(chat_id).delete()
        )
        return True
    
    async def delete_all_user_chats(
        self,
        user_id: str
    ) -> int:
        loop = asyncio.get_event_loop()
        
        docs = await loop.run_in_executor(
            None,
            lambda: list(
                self.db.collection(self.collection_name)
                .where("user_id", "==", user_id)
                .stream()
            )
        )
        
        count = 0
        for doc in docs:
            await loop.run_in_executor(
                None,
                lambda d=doc: d.reference.delete()
            )
            count += 1
        return count
    

    # ── Metrics Operations ────────────────────────
    async def log_metric(
        self,
        metric: MetricLog
    ) -> None:
        """Log a metric entry"""
        loop = asyncio.get_event_loop()
        doc_ref = self.db.collection(
            self.metrics_collection_name
        ).document(metric.id)
        
        await loop.run_in_executor(
            None,
            lambda: doc_ref.set(metric.model_dump())
        )
    
    async def get_metrics(
        self,
        user_id: str,
        limit  : int = 100
    ) -> List[MetricLog]:
        """Get recent metrics for user"""
        loop = asyncio.get_event_loop()
        
        docs = await loop.run_in_executor(
            None,
            lambda: list(
                self.db.collection(self.metrics_collection_name)
                .where("user_id", "==", user_id)
                .order_by(
                    "timestamp",
                    direction=firestore.Query.DESCENDING
                )
                .limit(limit)
                .stream()
            )
        )
        
        metrics = []
        for doc in docs:
            try:
                data = doc.to_dict()
                if isinstance(data.get("timestamp"), str):
                    data["timestamp"] = datetime.fromisoformat(
                        data["timestamp"]
                    )
                metrics.append(MetricLog(**data))
            except Exception as e:
                print(f"⚠️ Error parsing metric: {e}")
                continue
        return metrics
    
    async def get_metric(
        self,
        metric_id: str,
        user_id  : str
    ) -> Optional[MetricLog]:
        """Get single metric by ID"""
        loop = asyncio.get_event_loop()
        doc = await loop.run_in_executor(
            None,
            lambda: self.db.collection(
                self.metrics_collection_name
            ).document(metric_id).get()
        )
        
        if not doc.exists:
            return None
        
        data = doc.to_dict()
        if data.get("user_id") != user_id:
            return None
        
        if isinstance(data.get("timestamp"), str):
            data["timestamp"] = datetime.fromisoformat(
                data["timestamp"]
            )
        return MetricLog(**data)
    
    async def update_metric_rating(
        self,
        metric_id: str,
        user_id  : str,
        rating   : int
    ) -> bool:
        """Update user rating"""
        existing = await self.get_metric(metric_id, user_id)
        if not existing:
            return False
        
        loop = asyncio.get_event_loop()
        doc_ref = self.db.collection(
            self.metrics_collection_name
        ).document(metric_id)
        
        await loop.run_in_executor(
            None,
            lambda: doc_ref.update({"user_rating": rating})
        )
        return True

    async def update_metric_scores(
        self,
        metric_id: str,
        scores   : dict
    ) -> bool:
        """Update evaluation scores"""
        loop = asyncio.get_event_loop()
        doc_ref = self.db.collection(
            self.metrics_collection_name
        ).document(metric_id)
        
        await loop.run_in_executor(
            None,
            lambda: doc_ref.update({
                "faithfulness"     : scores.get("faithfulness"),
                "answer_relevancy" : scores.get("answer_relevancy"),
                "context_precision": scores.get("context_precision")
            })
        )
        return True





