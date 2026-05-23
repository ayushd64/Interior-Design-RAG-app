// app/layout.tsx
import type { Metadata } from "next"
import "./globals.css"
import { AuthProvider } from "./context/AuthContext"
import { ThemeProvider } from "./context/ThemeContext"

export const metadata: Metadata = {
  title      : "Interior Design AI Assistant",
  description: "AI powered interior design assistant for everyone"
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body>
        <ThemeProvider>
          <AuthProvider>
            {children}
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}

