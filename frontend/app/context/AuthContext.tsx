// app/context/AuthContext.tsx
"use client"

import { 
  createContext, 
  useContext, 
  useEffect, 
  useState,
  ReactNode 
} from "react"
import { 
  User,
  onAuthStateChanged,
  signOut as firebaseSignOut
} from "firebase/auth"
import { auth } from "../lib/firebase"

// ─────────────────────────────────────────────────
// Auth Context Type
// ─────────────────────────────────────────────────
interface AuthContextType {
  user        : User | null
  loading     : boolean
  signOut     : () => Promise<void>
  getIdToken  : () => Promise<string | null>
}

// ─────────────────────────────────────────────────
// Create Context
// ─────────────────────────────────────────────────
const AuthContext = createContext<AuthContextType>({
  user      : null,
  loading   : true,
  signOut   : async () => {},
  getIdToken: async () => null
})

// ─────────────────────────────────────────────────
// Auth Provider Component
// ─────────────────────────────────────────────────
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser]       = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  // ── Listen To Auth State Changes ──────────────
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(
      auth,
      (currentUser) => {
        setUser(currentUser)
        setLoading(false)
      }
    )

    return () => unsubscribe()
  }, [])

  // ── Sign Out ──────────────────────────────────
  const signOut = async () => {
    try {
      await firebaseSignOut(auth)
    } catch (error) {
      console.error("Sign out error:", error)
    }
  }

  // ── Get Firebase ID Token ─────────────────────
  const getIdToken = async (): Promise<string | null> => {
    if (!user) return null
    try {
      return await user.getIdToken()
    } catch (error) {
      console.error("Get token error:", error)
      return null
    }
  }

  return (
    <AuthContext.Provider value={{
      user,
      loading,
      signOut,
      getIdToken
    }}>
      {children}
    </AuthContext.Provider>
  )
}

// ─────────────────────────────────────────────────
// Custom Hook
// ─────────────────────────────────────────────────
export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider")
  }
  return context
}

