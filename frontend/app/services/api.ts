// app/services/api.ts
import axios from "axios"
import { ChatResponse, HistoryMessage, Chat, Message } from "../types"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL
  || "http://localhost:8000"

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json"
  }
})

// ─────────────────────────────────────────────────
// Auth Token Helper
// ─────────────────────────────────────────────────
// Stores token getter from AuthContext
let getTokenFn: (() => Promise<string | null>) | null = null

export const setAuthTokenGetter = (
  fn: () => Promise<string | null>
) => {
  getTokenFn = fn
}

// ── Add token to every request ────────────────────
api.interceptors.request.use(async (config) => {
  if (getTokenFn) {
    const token = await getTokenFn()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
  }
  return config
})




// ─────────────────────────────────────────────────
// CHAT MESSAGE API
// ─────────────────────────────────────────────────

// ── Regular Chat API ──────────────────────────────
export const sendMessage = async (
  question    : string,
  chat_history: HistoryMessage[] = []
): Promise<ChatResponse> => {
  const response = await api.post<ChatResponse>(
    "/api/chat",
    { question, chat_history }
  )
  return response.data
}

// ── Streaming Chat API ────────────────────────────
export const sendMessageStream = async (
  question    : string,
  chat_history: HistoryMessage[],
  onToken     : (token: string) => void,
  onMetadata  : (userLevel: string) => void,
  onDone      : () => void,
  onError     : (error: string) => void
): Promise<void> => {
  try {
    // Get auth token
const token = getTokenFn ? await getTokenFn() : null

const response = await fetch(
  `${API_BASE_URL}/api/chat/stream`,
  {
    method : "POST",
    headers: { 
      "Content-Type" : "application/json",
      "Authorization": token ? `Bearer ${token}` : ""
    },
    body   : JSON.stringify({
      question,
      chat_history
    })
  }
)



    if (!response.ok) {
      throw new Error("Stream request failed!")
    }

    const reader  = response.body?.getReader()
    const decoder = new TextDecoder()

    if (!reader) {
      throw new Error("No reader available!")
    }

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value)
      const lines = chunk.split("\n")

      for (const line of lines) {
        if (!line.startsWith("data: ")) continue

        const data = line.slice(6).trim()
        if (!data) continue

        try {
          const parsed = JSON.parse(data)

          switch (parsed.type) {
            case "metadata":
              onMetadata(parsed.user_level)
              break
            case "token":
              onToken(parsed.content)
              break
            case "done":
              onDone()
              break
            case "error":
              onError(parsed.content)
              break
          }
        } catch {
          // Skip invalid JSON
        }
      }
    }
  } catch (error) {
    onError(String(error))
  }
}

// ── Health Check API ──────────────────────────────
export const checkHealth = async (): Promise<boolean> => {
  try {
    const response = await api.get("/api/health")
    return response.data.status === "ok"
  } catch {
    return false
  }
}

// ─────────────────────────────────────────────────
// CHAT MANAGEMENT API (MongoDB!)
// ─────────────────────────────────────────────────

// ── Backend Chat Type (matches MongoDB) ───────────
interface BackendChat {
  id        : string
  title     : string
  messages  : BackendMessage[]
  created_at: string
  updated_at: string
}

interface BackendMessage {
  id        : string
  role      : "user" | "assistant"
  content   : string
  user_level?: string
  timestamp : string
}

// ── Helper: Convert backend to frontend format ────
const convertBackendChat = (chat: BackendChat): Chat => ({
  id       : chat.id,
  title    : chat.title,
  messages : chat.messages.map(msg => ({
    id        : msg.id,
    role      : msg.role,
    content   : msg.content,
    user_level: msg.user_level,
    timestamp : new Date(msg.timestamp)
  })),
  createdAt: new Date(chat.created_at)
})

// ── Get All Chats ─────────────────────────────────
export const fetchAllChats = async (): Promise<Chat[]> => {
  try {
    const response = await api.get<BackendChat[]>("/api/chats")
    return response.data.map(convertBackendChat)
  } catch (error) {
    console.error("Error fetching chats:", error)
    return []
  }
}

// ── Get Single Chat ───────────────────────────────
export const fetchChat = async (chatId: string): Promise<Chat | null> => {
  try {
    const response = await api.get<BackendChat>(`/api/chats/${chatId}`)
    return convertBackendChat(response.data)
  } catch (error) {
    console.error("Error fetching chat:", error)
    return null
  }
}

// ── Create New Chat ───────────────────────────────
export const createChatInDB = async (chat: Chat): Promise<Chat | null> => {
  try {
    const payload = {
      id        : chat.id,
      title     : chat.title,
      messages  : chat.messages.map(msg => ({
        id        : msg.id,
        role      : msg.role,
        content   : msg.content,
        user_level: msg.user_level,
        timestamp : msg.timestamp.toISOString()
      })),
      created_at: chat.createdAt.toISOString(),
      updated_at: chat.createdAt.toISOString()
    }
    
    const response = await api.post<BackendChat>(
      "/api/chats",
      payload
    )
    return convertBackendChat(response.data)
  } catch (error) {
    console.error("Error creating chat:", error)
    return null
  }
}

// ── Update Chat Title ─────────────────────────────
export const updateChatTitle = async (
  chatId : string,
  title  : string
): Promise<boolean> => {
  try {
    await api.patch(`/api/chats/${chatId}`, { title })
    return true
  } catch (error) {
    console.error("Error updating chat title:", error)
    return false
  }
}

// ── Add Message To Chat ───────────────────────────
export const addMessageToDB = async (
  chatId : string,
  message: Message
): Promise<boolean> => {
  try {
    const payload = {
      message: {
        id        : message.id,
        role      : message.role,
        content   : message.content,
        user_level: message.user_level,
        timestamp : message.timestamp.toISOString()
      }
    }
    
    await api.post(`/api/chats/${chatId}/messages`, payload)
    return true
  } catch (error) {
    console.error("Error adding message:", error)
    return false
  }
}

// ── Update Entire Chat Messages ───────────────────
export const updateChatMessages = async (
  chatId  : string,
  messages: Message[]
): Promise<boolean> => {
  try {
    const payload = {
      messages: messages.map(msg => ({
        id        : msg.id,
        role      : msg.role,
        content   : msg.content,
        user_level: msg.user_level,
        timestamp : msg.timestamp.toISOString()
      }))
    }
    
    await api.patch(`/api/chats/${chatId}`, payload)
    return true
  } catch (error) {
    console.error("Error updating messages:", error)
    return false
  }
}

// ── Delete Chat ───────────────────────────────────
export const deleteChatFromDB = async (chatId: string): Promise<boolean> => {
  try {
    await api.delete(`/api/chats/${chatId}`)
    return true
  } catch (error) {
    console.error("Error deleting chat:", error)
    return false
  }
}

