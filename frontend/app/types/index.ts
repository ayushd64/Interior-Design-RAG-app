// app/types/index.ts

export interface Message {
  id        : string
  role      : "user" | "assistant"
  content   : string
  user_level?: string
  imageUrl? : string
  timestamp : Date
}

export interface Chat {
  id       : string
  title    : string
  messages : Message[]
  createdAt: Date
}

// ── New! History message for API ──────────────────
export interface HistoryMessage {
  role   : "user" | "assistant"
  content: string
}

export interface ChatResponse {
  question  : string
  answer    : string
  user_level: string
  success   : boolean
}

export interface ApiError {
  detail: string
}