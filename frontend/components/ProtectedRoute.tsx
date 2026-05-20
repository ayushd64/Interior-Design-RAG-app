// components/ProtectedRoute.tsx
"use client"

import { useEffect, ReactNode } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "../app/context/AuthContext"
import { setAuthTokenGetter } from "../app/services/api"

interface ProtectedRouteProps {
  children: ReactNode
}

export default function ProtectedRoute({ 
  children 
}: ProtectedRouteProps) {
  const { user, loading, getIdToken } = useAuth()
  const router = useRouter()

  // ── Wire Up Auth Token To API ─────────────────
  useEffect(() => {
    setAuthTokenGetter(getIdToken)
  }, [getIdToken])

  // ── Redirect If Not Logged In ─────────────────
  useEffect(() => {
    if (!loading && !user) {
      router.push("/login")
    }
  }, [user, loading, router])

  // ── Loading Screen ────────────────────────────
  if (loading) {
    return (
      <div className="loading-screen">
        <div className="loading-spinner">🏠</div>
        <p>Loading...</p>
      </div>
    )
  }

  // ── Not Authenticated ─────────────────────────
  if (!user) {
    return (
      <div className="loading-screen">
        <div className="loading-spinner">🔐</div>
        <p>Redirecting to login...</p>
      </div>
    )
  }

  // ── Email Verification Check ──────────────────
  if (!user.emailVerified) {
    return (
      <div className="loading-screen">
        <div className="auth-card" style={{ maxWidth: 420 }}>
          <div style={{ textAlign: "center" }}>
            <div className="auth-logo">📧</div>
            <h1 className="auth-title">Verify Your Email</h1>
            <p className="auth-info">
              Please check <strong>{user.email}</strong> and click
              the verification link to access your account.
            </p>
            <p className="auth-info">
              After verifying, please sign out and sign back in.
            </p>
          </div>
        </div>
      </div>
    )
  }

  // ── User Authenticated & Verified ─────────────
  return <>{children}</>
}

