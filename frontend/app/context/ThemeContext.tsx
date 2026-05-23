// app/context/ThemeContext.tsx
"use client"

import {
  createContext,
  useContext,
  useEffect,
  useState,
  ReactNode
} from "react"

type Theme = "light" | "dark"

interface ThemeContextType {
  theme      : Theme
  toggleTheme: () => void
}

const ThemeContext = createContext<ThemeContextType>({
  theme      : "light",
  toggleTheme: () => {}
})

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>("light")

  // ── Load saved theme on mount ─────────────────
  useEffect(() => {
    const saved = localStorage.getItem("theme") as Theme | null
    if (saved) {
      setTheme(saved)
      document.documentElement.setAttribute("data-theme", saved)
    }
  }, [])

  // ── Toggle & persist ──────────────────────────
  const toggleTheme = () => {
    const newTheme = theme === "light" ? "dark" : "light"
    setTheme(newTheme)
    localStorage.setItem("theme", newTheme)

    if (newTheme === "dark") {
      document.documentElement.setAttribute("data-theme", "dark")
    } else {
      document.documentElement.removeAttribute("data-theme")
    }
  }

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

export const useTheme = () => useContext(ThemeContext)

