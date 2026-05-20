# database/crud.py
from typing import List, Optional
from database.factory import get_database
from database.models import (
    ChatModel,
    MessageModel,
    UpdateChatRequest
)

async def create_chat(chat: ChatModel) -> ChatModel:
    db = get_database()
    return await db.create_chat(chat)

async def get_user_chats(user_id: str) -> List[ChatModel]:
    db = get_database()
    return await db.get_user_chats(user_id)

async def get_chat(
    chat_id: str,
    user_id: str
) -> Optional[ChatModel]:
    db = get_database()
    return await db.get_chat(chat_id, user_id)

async def update_chat(
    chat_id: str,
    user_id: str,
    update : UpdateChatRequest
) -> Optional[ChatModel]:
    db = get_database()
    return await db.update_chat(chat_id, user_id, update)

async def add_message_to_chat(
    chat_id: str,
    user_id: str,
    message: MessageModel
) -> Optional[ChatModel]:
    db = get_database()
    return await db.add_message_to_chat(
        chat_id, user_id, message
    )

async def delete_chat(
    chat_id: str,
    user_id: str
) -> bool:
    db = get_database()
    return await db.delete_chat(chat_id, user_id)

async def delete_all_user_chats(user_id: str) -> int:
    db = get_database()
    return await db.delete_all_user_chats(user_id)

