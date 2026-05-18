"use client"

import { useState, KeyboardEvent } from "react"

interface InputBarProps {
  onSend    : (message: string) => void
  isLoading : boolean
}

export default function InputBar({ 
  onSend, 
  isLoading 
}: InputBarProps) {

  const [input, setInput] = useState("")

  // ── Handle Send ───────────────────────────────
  const handleSend = () => {
    if (!input.trim() || isLoading) return
    onSend(input.trim())
    setInput("")
  }

  // ── Handle Enter Key ──────────────────────────
  const handleKeyDown = (
    e: KeyboardEvent<HTMLTextAreaElement>
  ) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="input-bar">
      <div className="input-container">

        {/* ── Text Area ───────────────────────── */}
        <textarea
          className="input-textarea"
          placeholder="Ask me anything about interior design..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
          rows={1}
        />

        {/* ── Send Button ─────────────────────── */}
        <button
          className={`send-btn ${
            !input.trim() || isLoading
              ? "send-btn-disabled"
              : "send-btn-active"
          }`}
          onClick={handleSend}
          disabled={!input.trim() || isLoading}
        >
          {isLoading ? "⏳" : "🚀"}
        </button>

      </div>

      <p className="input-hint">
        Press Enter to send • Shift+Enter for new line
      </p>
    </div>
  )
}