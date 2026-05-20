// app/lib/firebase.ts
import { initializeApp, getApps } from "firebase/app"
import { getAuth, GoogleAuthProvider } from "firebase/auth"

// ── Your Firebase Configuration ───────────────────
const firebaseConfig = {
  apiKey           : "AIzaSyATw-IqmjaxU8JLLwshL7bNp3xqPllkAsg",
  authDomain       : "interior-design-rag-e4352.firebaseapp.com",
  projectId        : "interior-design-rag-e4352",
  storageBucket    : "interior-design-rag-e4352.firebasestorage.app",
  messagingSenderId: "277187833199",
  appId            : "1:277187833199:web:40a9f4450fd365a9970c9a",
  measurementId    : "G-EX1JDTMYEN"
}

// ── Initialize Firebase ──────────────────────────
const app = !getApps().length 
  ? initializeApp(firebaseConfig) 
  : getApps()[0]

// ── Auth Instance ────────────────────────────────
export const auth = getAuth(app)

// ── Google Provider ──────────────────────────────
export const googleProvider = new GoogleAuthProvider()
googleProvider.setCustomParameters({
  prompt: "select_account"
})

export default app

