"use client"

import { Chat } from "../app/types"

interface SidebarProps {
  chats         : Chat[]
  currentChatId : string | null
  onNewChat     : () => void
  onSelectChat  : (chatId: string) => void
  onDeleteChat  : (chatId: string) => void
}

export default function Sidebar({
  chats,
  currentChatId,
  onNewChat,
  onSelectChat,
  onDeleteChat
}: SidebarProps) {
  return (
    <div className="sidebar">

      {/* ── Logo ────────────────────────────── */}
      <div className="sidebar-logo">
        <span className="logo-icon">🏠</span>
        <div>
          <div className="logo-text">Interior AI</div>
          <div className="logo-subtitle">Design Assistant</div>
        </div>
      </div>

      {/* ── New Chat Button ──────────────────── */}
      <button
        onClick={onNewChat}
        className="new-chat-btn"
      >
        <span>✦</span>
        <span>New Conversation</span>
      </button>

      {/* ── Chat History ────────────────────── */}
      <div className="chat-history">
        <p className="history-label">Recent Conversations</p>

        {chats.length === 0 && (
          <p className="no-chats">
            No conversations yet!
            Start a new conversation above.
          </p>
        )}

        {chats.map((chat) => (
          <div
            key={chat.id}
            className={`chat-item ${
              currentChatId === chat.id
                ? "chat-item-active"
                : ""
            }`}
            onClick={() => onSelectChat(chat.id)}
          >
            <span className="chat-item-icon">💬</span>
            <span className="chat-item-title">
              {chat.title}
            </span>
            <button
              className="delete-btn"
              onClick={(e) => {
                e.stopPropagation()
                onDeleteChat(chat.id)
              }}
            >
              ✕
            </button>
          </div>
        ))}
      </div>

      {/* ── Footer ──────────────────────────── */}
      <div className="sidebar-footer">
        <p>Powered by <span>Llama 3.1</span></p>
        <p>Running <span>100% Locally</span></p>
      </div>

    </div>
  )
}