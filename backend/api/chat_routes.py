# api/chat_routes.py
from fastapi import APIRouter, HTTPException, Depends
from database.crud import (
    create_chat,
    get_user_chats,
    get_chat,
    update_chat,
    add_message_to_chat,
    delete_chat,
    delete_all_user_chats
)
from database.models import (
    ChatModel,
    UpdateChatRequest,
    AddMessageRequest
)
from auth.dependencies import get_current_user
from typing import List

router = APIRouter(prefix="/chats", tags=["Chats"])

# ── GET All User's Chats ──────────────────────────
@router.get("", response_model=List[ChatModel])
async def list_chats(
    user: dict = Depends(get_current_user)
):
    """Get all chats for authenticated user"""
    try:
        chats = await get_user_chats(user["uid"])
        return chats
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching chats: {str(e)}"
        )

# ── GET Single Chat ───────────────────────────────
@router.get("/{chat_id}", response_model=ChatModel)
async def get_single_chat(
    chat_id: str,
    user   : dict = Depends(get_current_user)
):
    chat = await get_chat(chat_id, user["uid"])
    if not chat:
        raise HTTPException(
            status_code=404,
            detail=f"Chat {chat_id} not found"
        )
    return chat

# ── CREATE Chat ───────────────────────────────────
@router.post("", response_model=ChatModel)
async def create_new_chat(
    chat: ChatModel,
    user: dict = Depends(get_current_user)
):
    """Create new chat (assigns to authenticated user)"""
    try:
        # Override user_id from token (security!)
        chat.user_id = user["uid"]
        created = await create_chat(chat)
        return created
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating chat: {str(e)}"
        )

# ── UPDATE Chat ───────────────────────────────────
@router.patch("/{chat_id}", response_model=ChatModel)
async def update_existing_chat(
    chat_id: str,
    update : UpdateChatRequest,
    user   : dict = Depends(get_current_user)
):
    updated = await update_chat(chat_id, user["uid"], update)
    if not updated:
        raise HTTPException(
            status_code=404,
            detail=f"Chat {chat_id} not found"
        )
    return updated

# ── ADD Message ───────────────────────────────────
@router.post("/{chat_id}/messages", response_model=ChatModel)
async def add_message(
    chat_id: str,
    request: AddMessageRequest,
    user   : dict = Depends(get_current_user)
):
    updated = await add_message_to_chat(
        chat_id,
        user["uid"],
        request.message
    )
    if not updated:
        raise HTTPException(
            status_code=404,
            detail=f"Chat {chat_id} not found"
        )
    return updated

# ── DELETE Chat ───────────────────────────────────
@router.delete("/{chat_id}")
async def delete_single_chat(
    chat_id: str,
    user   : dict = Depends(get_current_user)
):
    deleted = await delete_chat(chat_id, user["uid"])
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Chat {chat_id} not found"
        )
    return {
        "success": True,
        "message": f"Chat {chat_id} deleted!"
    }

# ── DELETE All User's Chats ───────────────────────
@router.delete("")
async def delete_all(
    user: dict = Depends(get_current_user)
):
    count = await delete_all_user_chats(user["uid"])
    return {
        "success": True,
        "message": f"Deleted {count} chats!"
    }

