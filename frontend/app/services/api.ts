// app/services/api.ts
import axios from "axios"
import { ChatResponse, HistoryMessage } from "../types"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL
  || "http://localhost:8000"

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json"
  }
})

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

// ── Streaming Chat API With Memory ───────────────
export const sendMessageStream = async (
  question    : string,
  chat_history: HistoryMessage[],      // ← Added!
  onToken     : (token: string) => void,
  onMetadata  : (userLevel: string) => void,
  onDone      : () => void,
  onError     : (error: string) => void
): Promise<void> => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/chat/stream`,
      {
        method : "POST",
        headers: { "Content-Type": "application/json" },
        body   : JSON.stringify({ 
          question, 
          chat_history      // ← Send history!
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