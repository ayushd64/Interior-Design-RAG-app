// app/login/page.tsx
"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import {
  signInWithEmailAndPassword,
  signInWithPopup,
  sendEmailVerification
} from "firebase/auth"
import { auth, googleProvider } from "../lib/firebase"

export default function LoginPage() {
  const router = useRouter()
  
  const [email, setEmail]       = useState("")
  const [password, setPassword] = useState("")
  const [error, setError]       = useState("")
  const [loading, setLoading]   = useState(false)
  const [needsVerification, setNeedsVerification] = useState(false)

  // ── Email/Password Sign In ────────────────────
  const handleEmailSignIn = async (
    e: React.FormEvent
  ) => {
    e.preventDefault()
    setError("")
    setLoading(true)

    try {
      const userCredential = await signInWithEmailAndPassword(
        auth,
        email,
        password
      )

      // Check email verification
      if (!userCredential.user.emailVerified) {
        setNeedsVerification(true)
        await auth.signOut()
        setLoading(false)
        return
      }

      router.push("/")

    } catch (err: any) {
      console.error("Sign in error:", err)
      
      if (err.code === "auth/invalid-credential") {
        setError("Invalid email or password!")
      } else if (err.code === "auth/user-not-found") {
        setError("No account found with this email!")
      } else if (err.code === "auth/wrong-password") {
        setError("Incorrect password!")
      } else {
        setError(err.message || "Sign in failed!")
      }
      
      setLoading(false)
    }
  }

  // ── Google Sign In ────────────────────────────
  const handleGoogleSignIn = async () => {
    setError("")
    setLoading(true)

    try {
      await signInWithPopup(auth, googleProvider)
      router.push("/")
    } catch (err: any) {
      console.error("Google sign in error:", err)
      setError(err.message || "Google sign in failed!")
      setLoading(false)
    }
  }

  // ── Resend Verification ───────────────────────
  const handleResendVerification = async () => {
    try {
      const userCredential = await signInWithEmailAndPassword(
        auth, email, password
      )
      await sendEmailVerification(userCredential.user)
      await auth.signOut()
      setError("Verification email sent! Check your inbox.")
    } catch (err: any) {
      setError("Failed to send verification email")
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        
        {/* ── Header ─────────────────────────── */}
        <div className="auth-header">
          <div className="auth-logo">🏠</div>
          <h1 className="auth-title">Welcome Back</h1>
          <p className="auth-subtitle">
            Sign in to your Interior Design AI account
          </p>
        </div>

        {/* ── Email Verification Banner ──────── */}
        {needsVerification && (
          <div className="auth-warning">
            <p>⚠️ Please verify your email first!</p>
            <button 
              onClick={handleResendVerification}
              className="auth-link-btn"
            >
              Resend verification email
            </button>
          </div>
        )}

        {/* ── Error Message ──────────────────── */}
        {error && (
          <div className="auth-error">
            {error}
          </div>
        )}

        {/* ── Login Form ─────────────────────── */}
        <form onSubmit={handleEmailSignIn} className="auth-form">
          <div className="auth-input-group">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
              disabled={loading}
            />
          </div>

          <div className="auth-input-group">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              disabled={loading}
            />
          </div>

          <button 
            type="submit" 
            className="auth-btn auth-btn-primary"
            disabled={loading}
          >
            {loading ? "Signing in..." : "Sign In"}
          </button>
        </form>

        {/* ── Divider ────────────────────────── */}
        <div className="auth-divider">
          <span>OR</span>
        </div>

        {/* ── Google Sign In ─────────────────── */}
        <button 
          onClick={handleGoogleSignIn}
          className="auth-btn auth-btn-google"
          disabled={loading}
        >
          <span>🌐</span>
          Continue with Google
        </button>

        {/* ── Footer ─────────────────────────── */}
        <div className="auth-footer">
          <p>
            Don&apos;t have an account?{" "}
            <Link href="/register" className="auth-link">
              Sign up
            </Link>
          </p>
        </div>

      </div>
    </div>
  )
}

