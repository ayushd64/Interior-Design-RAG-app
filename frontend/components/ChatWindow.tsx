"use client"

import { useEffect, useRef } from "react"
import MessageBubble from "./MessageBubble"
import { Message } from "../app/types"

interface ChatWindowProps {
  messages   : Message[]
  isLoading  : boolean
  streamingId: string | null
  onSend     : (message: string) => void  // ← Add this!
}

export default function ChatWindow({
  messages,
  isLoading,
  streamingId,
  onSend                                  // ← Add this!
}: ChatWindowProps) {

  // ── Auto scroll to bottom ─────────────────────
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: "smooth"
    })
  }, [messages, isLoading])

  // ── Suggestion Cards Data ─────────────────────
  const suggestions = [
    {
      icon : "💡",
      text : "How do I make my living room cozy?",
    },
    {
      icon : "🎨",
      text : "What colors work well together?",
    },
    {
      icon : "🪑",
      text : "How to arrange furniture in small space?",
    },
    {
      icon : "🏛️",
      text : "What is Bauhaus design movement?",
    }
  ]

  return (
    <div className="chat-window">

      {/* ── Welcome Message ───────────────────── */}
{messages.length === 0 && (
  <div className="welcome">
    <div className="welcome-icon">🏠</div>
    <h1 className="welcome-title">
      Your <span>Design</span> Assistant
    </h1>
    <div className="welcome-divider"></div>
    <p className="welcome-subtitle">
      Whether you are decorating your first home
      or designing a luxury space, I am here to
      inspire and guide you every step of the way.
    </p>

    {/* ── Suggestion Cards ──────────────── */}
    <div className="suggestions">
      {suggestions.map((suggestion, index) => (
        <div
          key={index}
          className="suggestion-card"
          onClick={() => {
            if (!isLoading) {
              onSend(suggestion.text)
            }
          }}
          style={{
            cursor : isLoading ? "not-allowed" : "pointer",
            opacity: isLoading ? 0.5 : 1
          }}
        >
          {suggestion.icon} {suggestion.text}
        </div>
      ))}
    </div>
  </div>
)}

      {/* ── Messages ──────────────────────────── */}
      {messages.map((message) => (
        <MessageBubble
          key={message.id}
          message={message}
          isStreaming={message.id === streamingId}
        />
      ))}

      {/* ── Initial Loading Indicator ─────────── */}
      {isLoading &&
       !streamingId && (
        <div className="message-wrapper message-assistant">
          <div className="avatar">🏠</div>
          <div className="bubble bubble-assistant">
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      )}

      {/* ── Scroll anchor ─────────────────────── */}
      <div ref={bottomRef} />

    </div>
  )
}
