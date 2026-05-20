// app/layout.tsx
import type { Metadata } from "next"
import "./globals.css"
import { AuthProvider } from "./context/AuthContext"

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
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  )
}

