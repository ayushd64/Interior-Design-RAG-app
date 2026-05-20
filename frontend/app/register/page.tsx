// app/register/page.tsx
"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import {
  createUserWithEmailAndPassword,
  sendEmailVerification,
  signInWithPopup,
  updateProfile
} from "firebase/auth"
import { auth, googleProvider } from "../lib/firebase"

export default function RegisterPage() {
  const router = useRouter()
  
  const [name, setName]                 = useState("")
  const [email, setEmail]               = useState("")
  const [password, setPassword]         = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [error, setError]               = useState("")
  const [loading, setLoading]           = useState(false)
  const [success, setSuccess]           = useState(false)

  // ── Email/Password Sign Up ────────────────────
  const handleEmailSignUp = async (
    e: React.FormEvent
  ) => {
    e.preventDefault()
    setError("")

    // Validate passwords match
    if (password !== confirmPassword) {
      setError("Passwords don't match!")
      return
    }

    // Validate password length
    if (password.length < 6) {
      setError("Password must be at least 6 characters!")
      return
    }

    setLoading(true)

    try {
      // Create user
      const userCredential = await createUserWithEmailAndPassword(
        auth, email, password
      )

      // Set display name
      if (name) {
        await updateProfile(userCredential.user, {
          displayName: name
        })
      }

      // Send verification email
      await sendEmailVerification(userCredential.user)

      // Sign out so they must verify first
      await auth.signOut()

      setSuccess(true)
      setLoading(false)

    } catch (err: any) {
      console.error("Sign up error:", err)
      
      if (err.code === "auth/email-already-in-use") {
        setError("Email already in use!")
      } else if (err.code === "auth/weak-password") {
        setError("Password is too weak!")
      } else if (err.code === "auth/invalid-email") {
        setError("Invalid email format!")
      } else {
        setError(err.message || "Sign up failed!")
      }
      
      setLoading(false)
    }
  }

  // ── Google Sign Up ────────────────────────────
  const handleGoogleSignUp = async () => {
    setError("")
    setLoading(true)

    try {
      await signInWithPopup(auth, googleProvider)
      router.push("/")
    } catch (err: any) {
      console.error("Google sign up error:", err)
      setError(err.message || "Google sign up failed!")
      setLoading(false)
    }
  }

  // ── Success Screen ────────────────────────────
  if (success) {
    return (
      <div className="auth-container">
        <div className="auth-card">
          <div className="auth-success">
            <div className="auth-success-icon">📧</div>
            <h1 className="auth-title">Check Your Email!</h1>
            <p className="auth-subtitle">
              We sent a verification link to <strong>{email}</strong>
            </p>
            <p className="auth-info">
              Please verify your email then sign in to continue.
            </p>
            <Link href="/login" className="auth-btn auth-btn-primary">
              Go to Sign In
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="auth-container">
      <div className="auth-card">

        <div className="auth-header">
          <div className="auth-logo">🏠</div>
          <h1 className="auth-title">Create Account</h1>
          <p className="auth-subtitle">
            Join Interior Design AI today
          </p>
        </div>

        {error && (
          <div className="auth-error">
            {error}
          </div>
        )}

        <form onSubmit={handleEmailSignUp} className="auth-form">
          <div className="auth-input-group">
            <label>Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="John Doe"
              disabled={loading}
            />
          </div>

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
              placeholder="At least 6 characters"
              required
              disabled={loading}
            />
          </div>

          <div className="auth-input-group">
            <label>Confirm Password</label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Re-enter password"
              required
              disabled={loading}
            />
          </div>

          <button 
            type="submit" 
            className="auth-btn auth-btn-primary"
            disabled={loading}
          >
            {loading ? "Creating account..." : "Sign Up"}
          </button>
        </form>

        <div className="auth-divider">
          <span>OR</span>
        </div>

        <button 
          onClick={handleGoogleSignUp}
          className="auth-btn auth-btn-google"
          disabled={loading}
        >
          <span>🌐</span>
          Continue with Google
        </button>

        <div className="auth-footer">
          <p>
            Already have an account?{" "}
            <Link href="/login" className="auth-link">
              Sign in
            </Link>
          </p>
        </div>

      </div>
    </div>
  )
}

