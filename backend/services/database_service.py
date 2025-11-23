"""
Database Service for Supabase Integration
Handles chat history and market data persistence
"""

import os
import json
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta, timezone
from uuid import uuid4
import asyncio
from supabase.aio import create_client, AsyncClient
from dotenv import load_dotenv

load_dotenv()


class DatabaseService:
    """Service for managing database operations with Supabase"""
    
    def __init__(self):
        """Initialize Supabase client"""
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase URL and key must be set in environment variables")
        
        self.client: AsyncClient = create_client(self.supabase_url, self.supabase_key)
        
    # ============ Chat History Methods ============
    
    async def create_conversation(self, user_id: Optional[str] = None, metadata: Dict = None) -> str:
        """Create a new conversation session"""
        try:
            data = {
                "user_id": user_id,
                "metadata": metadata or {}
            }
            
            response = await self.client.table("conversations").insert(data).execute()
            return response.data[0]["id"]
        except Exception as e:
            print(f"Error creating conversation: {e}")
            return str(uuid4())  # Return local UUID if DB fails
    
    async def end_conversation(self, conversation_id: str) -> bool:
        """Mark a conversation as ended"""
        try:
            await self.client.table("conversations").update({
                "ended_at": datetime.now(timezone.utc).isoformat()
            }).eq("id", conversation_id).execute()
            return True
        except Exception as e:
            print(f"Error ending conversation: {e}")
            return False
    
    async def save_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Optional[str]:
        """Save a message to the database"""
        try:
            data = {
                "conversation_id": conversation_id,
                "role": role,
                "content": content,
                "provider": provider,
                "model": model,
                "metadata": metadata or {}
            }
            
            response = await self.client.table("messages").insert(data).execute()
            return response.data[0]["id"]
        except Exception as e:
            print(f"Error saving message: {e}")
            return None
    
    async def get_conversation_history(
        self, 
        conversation_id: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict]:
        """Retrieve conversation history"""
        try:
            query = self.client.table("messages").select("*")
            
            if conversation_id:
                query = query.eq("conversation_id", conversation_id)
            elif user_id:
                # Get messages from user's conversations
                conv_response = await self.client.table("conversations").select("id").eq("user_id", user_id).execute()
                conv_ids = [c["id"] for c in conv_response.data]
                query = query.in_("conversation_id", conv_ids)
            
            response = await query.order("timestamp", desc=True).limit(limit).offset(offset).execute()
            return response.data
        except Exception as e:
            print(f"Error retrieving conversation history: {e}")
            return []
    
    async def get_recent_conversations(
        self, 
        user_id: Optional[str] = None,
        days: int = 7,
        limit: int = 10
    ) -> List[Dict]:
        """Get recent conversations with summary"""
        try:
            cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
            query = self.client.table("conversations").select("*, messages(count)")
            
            if user_id:
                query = query.eq("user_id", user_id)
            
            response = await query.gte("started_at", cutoff_date).order("started_at", desc=True).limit(limit).execute()
            return response.data
        except Exception as e:
            print(f"Error retrieving recent conversations: {e}")
            return []
    
    # ============ Market Data Methods ============
    
    async def save_market_candles(
        self,
        symbol: str,
        timeframe: str,
        candles: List[Dict],
        source: str = "alpaca"
    ) -> int:
        """Save multiple candles to database (batch insert)"""
        try:
            data = []
            for candle in candles:
                data.append({
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "timestamp": candle.get("timestamp") or candle.get("time"),
                    "open": float(candle["open"]),
                    "high": float(candle["high"]),
                    "low": float(candle["low"]),
                    "close": float(candle["close"]),
                    "volume": int(candle.get("volume", 0)),
                    "source": source
                })
            
            # Upsert to handle duplicates
            response = await self.client.table("market_candles").upsert(data).execute()
            return len(response.data)
        except Exception as e:
            print(f"Error saving market candles: {e}")
            return 0
    
    async def get_market_candles(
        self,
        symbol: str,
        timeframe: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 500
    ) -> List[Dict]:
        """Retrieve market candles from cache"""
        try:
            query = self.client.table("market_candles").select("*").eq("symbol", symbol).eq("timeframe", timeframe)
            
            if start_time:
                query = query.gte("timestamp", start_time.isoformat())
            if end_time:
                query = query.lte("timestamp", end_time.isoformat())
            
            response = await query.order("timestamp", desc=False).limit(limit).execute()
            return response.data
        except Exception as e:
            print(f"Error retrieving market candles: {e}")
            return []
    
    async def save_market_news(
        self,
        articles: List[Dict],
        symbol: Optional[str] = None
    ) -> int:
        """Save news articles to database"""
        try:
            data = []
            for article in articles:
                data.append({
                    "symbol": symbol,
                    "headline": article.get("headline") or article.get("title"),
                    "content": article.get("content") or article.get("description"),
                    "summary": article.get("summary"),
                    "source": article.get("source", "unknown"),
                    "source_url": article.get("url") or article.get("link"),
                    "published_at": article.get("published_at") or article.get("pubDate") or datetime.now(timezone.utc).isoformat(),
                    "sentiment_score": article.get("sentiment_score"),
                    "relevance_score": article.get("relevance_score"),
                    "metadata": {
                        "author": article.get("author"),
                        "images": article.get("images", []),
                        "symbols": article.get("symbols", [])
                    }
                })
            
            response = await self.client.table("market_news").insert(data).execute()
            return len(response.data)
        except Exception as e:
            print(f"Error saving market news: {e}")
            return 0
    
    async def get_market_news(
        self,
        symbol: Optional[str] = None,
        days: int = 7,
        limit: int = 20
    ) -> List[Dict]:
        """Retrieve cached news articles"""
        try:
            cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
            query = self.client.table("market_news").select("*")
            
            if symbol:
                query = query.eq("symbol", symbol)
            
            response = await query.gte("published_at", cutoff_date).order("published_at", desc=True).limit(limit).execute()
            return response.data
        except Exception as e:
            print(f"Error retrieving market news: {e}")
            return []
    
    # ============ User Data Methods ============
    
    async def save_user_drawing(
        self,
        user_id: Optional[str],
        symbol: str,
        drawing_type: str,
        data: Dict,
        conversation_id: Optional[str] = None
    ) -> Optional[str]:
        """Save a user's chart drawing"""
        try:
            drawing_data = {
                "user_id": user_id,
                "conversation_id": conversation_id,
                "symbol": symbol,
                "type": drawing_type,
                "data": data
            }
            
            response = await self.client.table("user_drawings").insert(drawing_data).execute()
            return response.data[0]["id"]
        except Exception as e:
            print(f"Error saving user drawing: {e}")
            return None
    
    async def get_user_drawings(
        self,
        user_id: Optional[str] = None,
        symbol: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """Retrieve user's chart drawings"""
        try:
            query = self.client.table("user_drawings").select("*")
            
            if user_id:
                query = query.eq("user_id", user_id)
            if symbol:
                query = query.eq("symbol", symbol)
            
            response = await query.order("created_at", desc=True).limit(limit).execute()
            return response.data
        except Exception as e:
            print(f"Error retrieving user drawings: {e}")
            return []
    
    async def save_user_watchlist(
        self,
        user_id: Optional[str],
        symbols: List[str],
        name: str = "Default"
    ) -> bool:
        """Save or update user's watchlist"""
        try:
            # Try to update existing watchlist
            existing = await self.client.table("user_watchlists").select("id").eq("user_id", user_id).eq("name", name).execute()
            
            if existing.data:
                # Update existing
                await self.client.table("user_watchlists").update({
                    "symbols": symbols,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }).eq("id", existing.data[0]["id"]).execute()
            else:
                # Create new
                await self.client.table("user_watchlists").insert({
                    "user_id": user_id,
                    "name": name,
                    "symbols": symbols
                }).execute()
            
            return True
        except Exception as e:
            print(f"Error saving user watchlist: {e}")
            return False
    
    async def get_user_watchlist(
        self,
        user_id: Optional[str],
        name: str = "Default"
    ) -> List[str]:
        """Get user's watchlist symbols"""
        try:
            response = await self.client.table("user_watchlists").select("symbols").eq("user_id", user_id).eq("name", name).eq("is_active", True).execute()
            
            if response.data:
                return response.data[0]["symbols"]
            return []
        except Exception as e:
            print(f"Error retrieving user watchlist: {e}")
            return []
    
    # ============ Analytics Methods ============
    
    async def log_query(
        self,
        user_id: Optional[str],
        query_type: str,
        query_content: str,
        symbol: Optional[str] = None,
        response_time_ms: Optional[int] = None,
        data_source: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> bool:
        """Log a query for analytics"""
        try:
            data = {
                "user_id": user_id,
                "query_type": query_type,
                "query_content": query_content[:500],  # Limit content length
                "symbol": symbol,
                "response_time_ms": response_time_ms,
                "data_source": data_source,
                "success": success,
                "error_message": error_message
            }
            
            await self.client.table("query_analytics").insert(data).execute()
            return True
        except Exception as e:
            print(f"Error logging query: {e}")
            return False

    async def log_request_event(
        self,
        event: str,
        telemetry: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Persist enriched request telemetry for auditing."""
        try:
            data = {
                "event": event,
                "request_id": telemetry.get("request_id"),
                "path": telemetry.get("path"),
                "method": telemetry.get("method"),
                "client_ip": telemetry.get("client_ip"),
                "forwarded_for": telemetry.get("forwarded_for"),
                "user_agent": telemetry.get("user_agent"),
                "session_id": telemetry.get("session_id"),
                "user_id": telemetry.get("user_id"),
                "duration_ms": telemetry.get("duration_ms"),
                "cost_summary": telemetry.get("cost_summary"),
                "payload": metadata or {},
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            await self.client.table("request_logs").insert(data).execute()
            return True
        except Exception as e:
            print(f"Error logging request event: {e}")
            return False
    
    async def get_query_stats(
        self,
        user_id: Optional[str] = None,
        days: int = 30
    ) -> Dict:
        """Get query statistics"""
        try:
            cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
            query = self.client.table("query_analytics").select("*")
            
            if user_id:
                query = query.eq("user_id", user_id)
            
            response = await query.gte("timestamp", cutoff_date).execute()
            
            if not response.data:
                return {}
            
            # Calculate statistics
            total_queries = len(response.data)
            success_rate = sum(1 for q in response.data if q["success"]) / total_queries * 100
            avg_response_time = sum(q["response_time_ms"] or 0 for q in response.data) / total_queries
            
            # Group by query type
            query_types = {}
            for q in response.data:
                qt = q["query_type"]
                query_types[qt] = query_types.get(qt, 0) + 1
            
            # Most queried symbols
            symbol_counts = {}
            for q in response.data:
                if q["symbol"]:
                    symbol_counts[q["symbol"]] = symbol_counts.get(q["symbol"], 0) + 1
            
            top_symbols = sorted(symbol_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                "total_queries": total_queries,
                "success_rate": round(success_rate, 2),
                "avg_response_time_ms": round(avg_response_time),
                "query_types": query_types,
                "top_symbols": top_symbols
            }
        except Exception as e:
            print(f"Error getting query stats: {e}")
            return {}
    
    # ============ Maintenance Methods ============
    
    async def cleanup_old_data(self) -> Dict[str, int]:
        """Clean up old data according to retention policy"""
        try:
            # This would normally call a stored procedure
            # For now, we'll implement basic cleanup
            
            deleted_counts = {
                "old_messages": 0,
                "old_candles": 0,
                "old_news": 0
            }
            
            # Delete messages older than 1 year
            year_ago = (datetime.now(timezone.utc) - timedelta(days=365)).isoformat()
            response = await self.client.table("messages").delete().lt("timestamp", year_ago).execute()
            deleted_counts["old_messages"] = len(response.data) if response.data else 0
            
            # Delete high-frequency candles older than 3 months
            three_months_ago = (datetime.now(timezone.utc) - timedelta(days=90)).isoformat()
            response = await self.client.table("market_candles").delete().in_("timeframe", ["1m", "5m", "15m"]).lt("timestamp", three_months_ago).execute()
            deleted_counts["old_candles"] = len(response.data) if response.data else 0
            
            # Delete news older than 6 months
            six_months_ago = (datetime.now(timezone.utc) - timedelta(days=180)).isoformat()
            response = await self.client.table("market_news").delete().lt("published_at", six_months_ago).execute()
            deleted_counts["old_news"] = len(response.data) if response.data else 0
            
            return deleted_counts
        except Exception as e:
            print(f"Error cleaning up old data: {e}")
            return {}


# Singleton instance
_db_service: Optional[DatabaseService] = None


def get_database_service() -> DatabaseService:
    """Get or create the database service singleton"""
    global _db_service
    if _db_service is None:
        _db_service = DatabaseService()
    return _db_service