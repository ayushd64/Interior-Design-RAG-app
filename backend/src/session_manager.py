from typing import Dict, List
from datetime import datetime

class Message:
    """Represents a single chat message"""
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content
        self.timestamp = datetime.now()

    def to_dict(self) -> dict:
        return {
            "role": self.role,
            "content": self.content
        }

class SessionManager:
    """
    Manages chat history for multiple sessions
    In-memory storage (can be replaced with database later)
    """
    def __init__(self, max_history: int = 10):
        """
        Args:
            max_history: Maximum number of message pairs to keep per session
        """
        self._sessions: Dict[str, List[Message]] = {}
        self.max_history = max_history

    def create_session(self, session_id: str) -> None:
        """Create a new session if not exists"""
        if session_id not in self._sessions:
            self._sessions[session_id] = []
            print(f"--- Created new session: {session_id} ---")

    def add_message(self, session_id: str, role: str, content: str) -> None:
        """Add a message to session history"""
        self.create_session(session_id)

        message = Message(role, content)
        self._sessions[session_id].append(message)

        # Keep only last N messages (pairs of user + assistant)
        if len(self._sessions[session_id]) > self.max_history * 2:
            self._sessions[session_id] = self._sessions[session_id][-self.max_history * 2:]

        print(f"--- Added {role} message to session {session_id} ---")

    def get_history(self, session_id: str) -> List[dict]:
        """Get formatted history for a session"""
        if session_id not in self._sessions:
            return []

        return [msg.to_dict() for msg in self._sessions[session_id]]

    def get_history_text(self, session_id: str) -> str:
        """Get history as formatted text for LLM context"""
        history = self.get_history(session_id)
        if not history:
            return ""

        formatted = []
        for msg in history:
            role = "User" if msg["role"] == "user" else "Assistant"
            formatted.append(f"{role}: {msg['content']}")

        return "\n".join(formatted)

    def clear_session(self, session_id: str) -> None:
        """Clear a specific session"""
        if session_id in self._sessions:
            self._sessions[session_id] = []
            print(f"--- Cleared session: {session_id} ---")

    def delete_session(self, session_id: str) -> None:
        """Delete a session completely"""
        if session_id in self._sessions:
            del self._sessions[session_id]
            print(f"--- Deleted session: {session_id} ---")

# ── Singleton Instance ─────────────────────────────
session_manager = SessionManager(max_history=10)