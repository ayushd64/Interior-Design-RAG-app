// app/page.tsx
"use client"

import { useState, useCallback } from "react"
import Sidebar from "../components/Sidebar"
import ChatWindow from "../components/ChatWindow"
import InputBar from "../components/InputBar"
import { Chat, Message, HistoryMessage } from "./types"
import { sendMessageStream } from "./services/api"

const generateId = () => Math.random().toString(36).substr(2, 9)

export default function Home() {

  const [chats, setChats]                 = useState<Chat[]>([])
  const [currentChatId, setCurrentChatId] = useState<string | null>(null)
  const [isLoading, setIsLoading]         = useState(false)
  const [streamingId, setStreamingId]     = useState<string | null>(null)

  const currentChat = chats.find(c => c.id === currentChatId)
  const messages    = currentChat?.messages || []

  // ── Build History From Current Chat ──────────
  const buildHistory = useCallback((
    chatMessages: Message[]
  ): HistoryMessage[] => {
    return chatMessages
      .filter(msg => msg.content !== "")
      .map(msg => ({
        role   : msg.role,
        content: msg.content
      }))
  }, [])

  const handleNewChat = useCallback(() => {
    const newChat: Chat = {
      id       : generateId(),
      title    : "New Chat",
      messages : [],
      createdAt: new Date()
    }
    setChats(prev => [newChat, ...prev])
    setCurrentChatId(newChat.id)
  }, [])

  const handleSelectChat = useCallback((chatId: string) => {
    setCurrentChatId(chatId)
  }, [])

  const handleDeleteChat = useCallback((chatId: string) => {
    setChats(prev => prev.filter(c => c.id !== chatId))
    if (currentChatId === chatId) {
      setCurrentChatId(null)
    }
  }, [currentChatId])

  const handleSend = useCallback(async (question: string) => {

    let chatId = currentChatId
    if (!chatId) {
      const newChat: Chat = {
        id       : generateId(),
        title    : question.slice(0, 30) + "...",
        messages : [],
        createdAt: new Date()
      }
      setChats(prev => [newChat, ...prev])
      setCurrentChatId(newChat.id)
      chatId = newChat.id
    }

    // ── Get current messages for history ──────
    const currentMessages = chats.find(
      c => c.id === chatId
    )?.messages || []

    // ── Build history BEFORE adding new message ─
    const history = buildHistory(currentMessages)

    // ── Add User Message ──────────────────────
    const userMessage: Message = {
      id       : generateId(),
      role     : "user",
      content  : question,
      timestamp: new Date()
    }

    setChats(prev => prev.map(chat =>
      chat.id === chatId
        ? {
            ...chat,
            title   : chat.messages.length === 0
              ? question.slice(0, 30) + "..."
              : chat.title,
            messages: [...chat.messages, userMessage]
          }
        : chat
    ))

    // ── Create Empty Assistant Message ────────
    const assistantId = generateId()
    const assistantMessage: Message = {
      id        : assistantId,
      role      : "assistant",
      content   : "",
      user_level: undefined,
      timestamp : new Date()
    }

    setChats(prev => prev.map(chat =>
      chat.id === chatId
        ? {
            ...chat,
            messages: [...chat.messages, assistantMessage]
          }
        : chat
    ))

    setIsLoading(true)
    setStreamingId(assistantId)

    await sendMessageStream(
      question,
      history,              // ← Pass history!

      (token: string) => {
        setChats(prev => prev.map(chat =>
          chat.id === chatId
            ? {
                ...chat,
                messages: chat.messages.map(msg =>
                  msg.id === assistantId
                    ? { ...msg, content: msg.content + token }
                    : msg
                )
              }
            : chat
        ))
      },

      (userLevel: string) => {
        setChats(prev => prev.map(chat =>
          chat.id === chatId
            ? {
                ...chat,
                messages: chat.messages.map(msg =>
                  msg.id === assistantId
                    ? { ...msg, user_level: userLevel }
                    : msg
                )
              }
            : chat
        ))
      },

      () => {
        setIsLoading(false)
        setStreamingId(null)
        console.log("Stream complete!")
      },

      (error: string) => {
        console.error("Stream error:", error)
        setChats(prev => prev.map(chat =>
          chat.id === chatId
            ? {
                ...chat,
                messages: chat.messages.map(msg =>
                  msg.id === assistantId
                    ? {
                        ...msg,
                        content: "Sorry! Something went wrong. Please try again."
                      }
                    : msg
                )
              }
            : chat
        ))
        setIsLoading(false)
        setStreamingId(null)
      }
    )

  }, [currentChatId, chats, buildHistory])

  return (
    <main className="app-container">

      <Sidebar
        chats={chats}
        currentChatId={currentChatId}
        onNewChat={handleNewChat}
        onSelectChat={handleSelectChat}
        onDeleteChat={handleDeleteChat}
      />

      <div className="main-content">

        <div className="chat-header">
          <div>
            <div className="chat-header-title">
              Interior Design Assistant
            </div>
            <div className="chat-header-subtitle">
              Ask anything about interior design
            </div>
          </div>
          <div className="status-indicator">
            <div className="status-dot"></div>
            <span>AI Online</span>
          </div>
        </div>

        <ChatWindow
          messages={messages}
          isLoading={isLoading}
          streamingId={streamingId}
          onSend={handleSend}
        />

        <InputBar
          onSend={handleSend}
          isLoading={isLoading}
        />

      </div>

    </main>
  )
}