"""
Session Store for ChatKit Chart Context
========================================
Stores chart context keyed by session_id so custom actions can access it.

In-memory store with TTL cleanup (TODO: migrate to Redis for production scaling).
"""
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)

# In-memory store (session_id -> session_data)
# TODO: Replace with Redis for production (supports multiple backend instances)
_session_store: Dict[str, Dict[str, Any]] = {}


class SessionStore:
    """
    Session storage for ChatKit chart context
    
    Allows frontend to update chart context (symbol, timeframe) and
    backend custom actions to retrieve it during Agent Builder workflows.
    """
    
    @staticmethod
    def set_chart_context(session_id: str, chart_context: Dict[str, Any]) -> None:
        """
        Store chart context for a session
        
        Args:
            session_id: ChatKit session identifier
            chart_context: Dict with symbol, timeframe, snapshot_id, etc.
        """
        _session_store[session_id] = {
            'chart_context': chart_context,
            'updated_at': datetime.now().isoformat()
        }
        logger.info(f"✅ [SESSION] Stored chart context for {session_id}: {chart_context}")
    
    @staticmethod
    def get_chart_context(session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve chart context for a session
        
        Args:
            session_id: ChatKit session identifier
            
        Returns:
            Chart context dict or None if not found
        """
        session_data = _session_store.get(session_id)
        if session_data:
            logger.info(f"✅ [SESSION] Retrieved chart context for {session_id}: {session_data.get('chart_context')}")
            return session_data.get('chart_context')
        
        logger.warning(f"⚠️  [SESSION] No chart context found for {session_id}")
        return None
    
    @staticmethod
    def delete_session(session_id: str) -> bool:
        """
        Delete a session from the store
        
        Args:
            session_id: ChatKit session identifier
            
        Returns:
            True if session existed and was deleted, False otherwise
        """
        if session_id in _session_store:
            del _session_store[session_id]
            logger.info(f"🗑️  [SESSION] Deleted session {session_id}")
            return True
        return False
    
    @staticmethod
    def clear_old_sessions(max_age_hours: int = 24) -> int:
        """
        Clear sessions older than max_age_hours
        
        Args:
            max_age_hours: Maximum age in hours (default: 24)
            
        Returns:
            Number of sessions cleared
        """
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        old_sessions = [
            sid for sid, data in _session_store.items()
            if datetime.fromisoformat(data['updated_at']) < cutoff
        ]
        
        for sid in old_sessions:
            del _session_store[sid]
        
        if old_sessions:
            logger.info(f"🧹 [SESSION] Cleared {len(old_sessions)} old sessions (>{max_age_hours}h)")
        
        return len(old_sessions)
    
    @staticmethod
    def get_all_sessions() -> Dict[str, Dict[str, Any]]:
        """
        Get all active sessions (for debugging/monitoring)
        
        Returns:
            Dict of all sessions
        """
        return _session_store.copy()
    
    @staticmethod
    def get_session_count() -> int:
        """
        Get count of active sessions
        
        Returns:
            Number of active sessions
        """
        return len(_session_store)


# Singleton instance
session_store = SessionStore()


if __name__ == "__main__":
    # Test the session store
    logging.basicConfig(level=logging.INFO)
    
    # Test set and get
    session_store.set_chart_context("test_session_123", {
        "symbol": "TSLA",
        "timeframe": "1D",
        "snapshot_id": "snap_abc"
    })
    
    context = session_store.get_chart_context("test_session_123")
    print("Retrieved context:", context)
    assert context['symbol'] == "TSLA"
    
    # Test non-existent session
    none_context = session_store.get_chart_context("non_existent")
    assert none_context is None
    
    # Test clear old sessions
    print(f"Active sessions: {session_store.get_session_count()}")
    
    # Clean up
    session_store.delete_session("test_session_123")
    print(f"Active sessions after cleanup: {session_store.get_session_count()}")
    
    print("✅ All tests passed!")

