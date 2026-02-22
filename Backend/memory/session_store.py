"""Session Store - Conversation History and Session Management.

Manages:
- Session creation and retrieval
- Conversation history storage
- Multi-turn context
- Session expiration
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid
import json


class Session:
    """Represents a user session with conversation history."""
    
    def __init__(self, session_id: str = None, user_id: str = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.user_id = user_id
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.messages: List[Dict[str, Any]] = []
        self.context: Dict[str, Any] = {}  # Extracted context from conversation
        self.tool_history: List[Dict[str, Any]] = []
    
    def add_message(self, role: str, content: str, tool_calls: List = None):
        """Add a message to the conversation history."""
        self.messages.append({
            "role": role,
            "content": content,
            "tool_calls": tool_calls or [],
            "timestamp": datetime.now().isoformat()
        })
        self.last_activity = datetime.now()
    
    def add_tool_call(self, tool_name: str, arguments: Dict, result: Any):
        """Record a tool call."""
        self.tool_history.append({
            "tool": tool_name,
            "arguments": arguments,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
    
    def update_context(self, key: str, value: Any):
        """Update session context (extracted info from conversation)."""
        self.context[key] = value
        self.last_activity = datetime.now()
    
    def get_conversation_summary(self, max_messages: int = 10) -> str:
        """Get a summary of recent conversation for context."""
        recent = self.messages[-max_messages:]
        summary_parts = []
        
        for msg in recent:
            role = "User" if msg["role"] == "user" else "Assistant"
            content = msg["content"][:200] + "..." if len(msg["content"]) > 200 else msg["content"]
            summary_parts.append(f"{role}: {content}")
        
        return "\n".join(summary_parts)
    
    def get_context_prompt(self) -> str:
        """Get context as a prompt prefix."""
        if not self.context:
            return ""
        
        context_str = json.dumps(self.context, indent=2)
        return f"Previous conversation context:\n{context_str}\n\n"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "messages": self.messages,
            "context": self.context,
            "message_count": len(self.messages)
        }


class SessionStore:
    """In-memory session store with expiration."""
    
    SESSION_TIMEOUT_HOURS = 24
    
    def __init__(self):
        self._sessions: Dict[str, Session] = {}
    
    def create_session(self, user_id: str = None) -> Session:
        """Create a new session."""
        session = Session(user_id=user_id)
        self._sessions[session.session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by ID."""
        session = self._sessions.get(session_id)
        
        if session:
            # Check if expired
            if self._is_expired(session):
                self.delete_session(session_id)
                return None
            return session
        
        return None
    
    def get_or_create_session(self, session_id: str = None, user_id: str = None) -> Session:
        """Get existing session or create new one."""
        if session_id:
            session = self.get_session(session_id)
            if session:
                return session
        
        return self.create_session(user_id=user_id)
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False
    
    def _is_expired(self, session: Session) -> bool:
        """Check if a session is expired."""
        expiry = session.last_activity + timedelta(hours=self.SESSION_TIMEOUT_HOURS)
        return datetime.now() > expiry
    
    def cleanup_expired(self) -> int:
        """Remove expired sessions. Returns count of removed sessions."""
        expired = [
            sid for sid, session in self._sessions.items()
            if self._is_expired(session)
        ]
        for sid in expired:
            del self._sessions[sid]
        return len(expired)
    
    def list_sessions(self, user_id: str = None) -> List[Dict]:
        """List all sessions, optionally filtered by user."""
        sessions = []
        for session in self._sessions.values():
            if user_id is None or session.user_id == user_id:
                sessions.append({
                    "session_id": session.session_id,
                    "user_id": session.user_id,
                    "created_at": session.created_at.isoformat(),
                    "message_count": len(session.messages)
                })
        return sessions


# Global session store instance
_session_store: Optional[SessionStore] = None


def get_session_store() -> SessionStore:
    """Get or create the global session store."""
    global _session_store
    if _session_store is None:
        _session_store = SessionStore()
    return _session_store
