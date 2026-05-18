import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Interior Design AI Assistant",
  description: "AI powered interior design assistant for everyone",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  );
}