// components/Sidebar.tsx
"use client"

import { User } from "firebase/auth"
import { Chat } from "../app/types"
import { useTheme } from "../app/context/ThemeContext"

interface SidebarProps {
  chats         : Chat[]
  currentChatId : string | null
  onNewChat     : () => void
  onSelectChat  : (chatId: string) => void
  onDeleteChat  : (chatId: string) => void
  user          : User | null
  onSignOut     : () => Promise<void>
}

export default function Sidebar({
  chats,
  currentChatId,
  onNewChat,
  onSelectChat,
  onDeleteChat,
  user,
  onSignOut
}: SidebarProps) {

  const { theme, toggleTheme } = useTheme()

  // ── Get User Display Info ─────────────────────
  const displayName  = user?.displayName || "User"
  const email        = user?.email || ""
  const photoURL     = user?.photoURL
  const firstLetter  = displayName.charAt(0).toUpperCase()

  // ── Handle Sign Out ───────────────────────────
  const handleSignOut = async () => {
    const confirmed = confirm("Are you sure you want to sign out?")
    if (confirmed) {
      await onSignOut()
    }
  }

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

      {/* ── Theme Toggle ────────────────────── */} 
      <button onClick={toggleTheme} className="theme-toggle"> 
        {theme === "light" ? "🌙 Dark Mode" : "☀️ Light Mode"} 
      </button> 


      {/* ── Dashboard Link ──────────────────── */}
      <a href="/dashboard" className="dashboard-link">
        📊 View Dashboard
      </a>


      {/* ── User Profile ────────────────────── */}
      <div className="user-profile">
        <div className="user-avatar">
          {photoURL ? (
            <img src={photoURL} alt={displayName} />
          ) : (
            <span>{firstLetter}</span>
          )}
        </div>
        
        <div className="user-info">
          <div className="user-name">{displayName}</div>
          <div className="user-email">{email}</div>
        </div>

        <button
          onClick={handleSignOut}
          className="signout-btn"
          title="Sign out"
        >
          ⎋
        </button>
      </div>

    </div>
  )
}

