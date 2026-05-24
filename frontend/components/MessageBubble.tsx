"use client"

import ReactMarkdown from "react-markdown"
import { Message } from "../app/types"

interface MessageBubbleProps {
  message    : Message
  isStreaming: boolean
}

export default function MessageBubble({
  message,
  isStreaming
}: MessageBubbleProps) {

  const isUser = message.role === "user"

  // ── Format Time ───────────────────────────────
  const formatTime = (date: Date) => {
    return new Date(date).toLocaleTimeString([], {
      hour  : "2-digit",
      minute: "2-digit"
    })
  }

  // ── Get Badge Info ────────────────────────────
  const getBadge = () => {
    if (!message.user_level) return null

    switch(message.user_level) {
      case "EXPERT":
        return {
          label: "🎓 Expert Mode",
          class: "badge-expert"
        }
      case "BEGINNER":
        return {
          label: "👋 Beginner Mode",
          class: "badge-beginner"
        }
      case "OFF_TOPIC":
        return null
      default:
        return null
    }
  }

  const badge = getBadge()

  return (
    <div className={`message-wrapper ${
      isUser ? "message-user" : "message-assistant"
    }`}>

      {/* ── Avatar ────────────────────────────── */}
<div className={`avatar ${
  isUser ? "avatar-user" : "avatar-bot"
}`}>
  {isUser ? "👤" : "🏠"}
</div>

      {/* ── Bubble ────────────────────────────── */}
      <div className={`bubble ${
        isUser ? "bubble-user" : "bubble-assistant"
      }`}>

        {/* ── User Level Badge ────────────────── */}
        {!isUser && badge && (
          <div className={`level-badge ${badge.class}`}>
            {badge.label}
          </div>
        )}

        {/* ── Message Content ──────────────────── */}
        <div className="message-content">
          {isUser ? (
            <p>{message.content}</p>
          ) : (
            <>
              {/* ── Generated Image ──────────────── */}
              {message.imageUrl && (
                <div className="message-image-wrapper">
                  <img
                    src={message.imageUrl}
                    alt="Generated interior design"
                    className="message-image"
                    referrerPolicy="no-referrer"
                  />
                </div>
              )}

              <ReactMarkdown>
                {message.content}
              </ReactMarkdown>
              {/* ── Streaming Cursor ─────────────── */}
              {isStreaming && (
                <span className="streaming-cursor">▋</span>
              )}
            </>
          )}
        </div>

        {/* ── Timestamp ───────────────────────── */}
        {!isStreaming && (
          <div className="timestamp">
            {formatTime(message.timestamp)}
          </div>
        )}

      </div>
    </div>
  )
}