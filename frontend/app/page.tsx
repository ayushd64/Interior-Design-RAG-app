// app/page.tsx
"use client"

import { useState, useCallback, useEffect } from "react"
import Sidebar from "../components/Sidebar"
import ChatWindow from "../components/ChatWindow"
import InputBar from "../components/InputBar"
import ProtectedRoute from "../components/ProtectedRoute"
import { useAuth } from "./context/AuthContext"
import { Chat, Message, HistoryMessage } from "./types"
import {
  sendMessageStream,
  fetchAllChats,
  createChatInDB,
  updateChatTitle,
  addMessageToDB,
  deleteChatFromDB
} from "./services/api"

const generateId = () => Math.random().toString(36).substr(2, 9)

// ── Main App Component (wrapped in auth) ──────
function HomeContent() {

  const { user, signOut } = useAuth()
  
  const [chats, setChats]                 = useState<Chat[]>([])
  const [currentChatId, setCurrentChatId] = useState<string | null>(null)
  const [isLoading, setIsLoading]         = useState(false)
  const [streamingId, setStreamingId]     = useState<string | null>(null)
  const [isInitialized, setIsInitialized] = useState(false)

  // ── Load Chats From DB On Mount ───────────────
  useEffect(() => {
    const loadChats = async () => {
      console.log("Loading chats from database...")
      try {
        const loadedChats = await fetchAllChats()
        setChats(loadedChats)
      } catch (err) {
        console.error("Failed to load chats:", err)
      } finally {
        setIsInitialized(true)
      }
    }
    
    loadChats()
  }, [])

  const currentChat = chats.find(c => c.id === currentChatId)
  const messages    = currentChat?.messages || []

  // ── Build History ─────────────────────────────
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

  // ── New Chat ──────────────────────────────────
  const handleNewChat = useCallback(() => {
    setCurrentChatId(null)
  }, [])

  // ── Select Chat ───────────────────────────────
  const handleSelectChat = useCallback((chatId: string) => {
    setCurrentChatId(chatId)
  }, [])

  // ── Delete Chat ───────────────────────────────
  const handleDeleteChat = useCallback(async (chatId: string) => {
    setChats(prev => prev.filter(c => c.id !== chatId))
    if (currentChatId === chatId) {
      setCurrentChatId(null)
    }
    await deleteChatFromDB(chatId)
  }, [currentChatId])

  // ── Send Message ──────────────────────────────
  const handleSend = useCallback(async (question: string) => {
    let chatId = currentChatId
    let isNewChat = false

    if (!chatId) {
      const newChat: Chat = {
        id       : generateId(),
        title    : question.slice(0, 30) + (question.length > 30 ? "..." : ""),
        messages : [],
        createdAt: new Date()
      }
      
      isNewChat = true
      chatId = newChat.id
      
      setChats(prev => [newChat, ...prev])
      setCurrentChatId(newChat.id)
      
      await createChatInDB(newChat)
    }

    const currentMessages = chats.find(
      c => c.id === chatId
    )?.messages || []
    
    const history = buildHistory(currentMessages)

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
              ? question.slice(0, 30) + (question.length > 30 ? "..." : "")
              : chat.title,
            messages: [...chat.messages, userMessage]
          }
        : chat
    ))

    await addMessageToDB(chatId, userMessage)
    
    if (isNewChat) {
      await updateChatTitle(
        chatId,
        question.slice(0, 30) + (question.length > 30 ? "..." : "")
      )
    }

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

    let finalContent = ""
    let finalUserLevel = ""

    await sendMessageStream(
      question,
      history,

      (token: string) => {
        finalContent += token
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
        finalUserLevel = userLevel
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

      async () => {
        setIsLoading(false)
        setStreamingId(null)
        
        const completeMessage: Message = {
          id        : assistantId,
          role      : "assistant",
          content   : finalContent,
          user_level: finalUserLevel,
          timestamp : new Date()
        }
        
        await addMessageToDB(chatId!, completeMessage)
        console.log("Message saved!")
      },

      async (error: string) => {
        console.error("Stream error:", error)
        
        const errorContent = "Sorry! Something went wrong. Please try again."
        
        setChats(prev => prev.map(chat =>
          chat.id === chatId
            ? {
                ...chat,
                messages: chat.messages.map(msg =>
                  msg.id === assistantId
                    ? {
                        ...msg,
                        content: errorContent
                      }
                    : msg
                )
              }
            : chat
        ))
        
        const errorMessage: Message = {
          id        : assistantId,
          role      : "assistant",
          content   : errorContent,
          timestamp : new Date()
        }
        
        await addMessageToDB(chatId!, errorMessage)
        
        setIsLoading(false)
        setStreamingId(null)
      }
    )

  }, [currentChatId, chats, buildHistory])

  // ── Loading State ─────────────────────────────
  if (!isInitialized) {
    return (
      <div className="loading-screen">
        <div className="loading-spinner">🏠</div>
        <p>Loading your conversations...</p>
      </div>
    )
  }

  return (
    <main className="app-container">

      <Sidebar
        chats={chats}
        currentChatId={currentChatId}
        onNewChat={handleNewChat}
        onSelectChat={handleSelectChat}
        onDeleteChat={handleDeleteChat}
        user={user}              
        onSignOut={signOut}      
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

// ── Wrap In Protected Route ────────────────────
export default function Home() {
  return (
    <ProtectedRoute>
      <HomeContent />
    </ProtectedRoute>
  )
}

