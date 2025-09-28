"""
Pattern Repository for Phase 4
Database abstraction layer for pattern events
"""

import logging
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone, timedelta
from uuid import uuid4
from supabase import create_client, Client
import os

logger = logging.getLogger(__name__)

class PatternRepository:
    """
    Repository for pattern events database operations
    Abstracts Supabase/PostgreSQL interactions
    """
    
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if self.supabase_url and self.supabase_key:
            self.client: Client = create_client(self.supabase_url, self.supabase_key)
        else:
            logger.warning("Supabase credentials not configured - pattern persistence disabled")
            self.client = None
    
    async def create_pattern(self, pattern_data: Dict[str, Any]) -> Optional[str]:
        """
        Create a new pattern event
        
        Args:
            pattern_data: Pattern metadata
            
        Returns:
            Pattern ID if successful, None otherwise
        """
        if not self.client:
            return None
            
        try:
            # Prepare data for insertion
            pattern_id = str(uuid4())
            insert_data = {
                "id": pattern_id,
                "symbol": pattern_data.get("symbol"),
                "timeframe": pattern_data.get("timeframe", "1D"),
                "pattern_type": pattern_data.get("pattern_type"),
                "status": pattern_data.get("status", "pending"),
                "confidence": pattern_data.get("confidence", 0.5),
                "target": pattern_data.get("target"),
                "entry": pattern_data.get("entry"),
                "stoploss": pattern_data.get("stoploss"),
                "support": pattern_data.get("support"),
                "resistance": pattern_data.get("resistance"),
                "draw_commands": json.dumps(pattern_data.get("draw_commands", [])),
                "metadata": json.dumps(pattern_data.get("metadata", {})),
                "snapshot_url": pattern_data.get("snapshot_url"),
                "operator_id": pattern_data.get("operator_id"),
                "auto_generated": pattern_data.get("auto_generated", False)
            }
            
            # Remove None values
            insert_data = {k: v for k, v in insert_data.items() if v is not None}
            
            # Insert into database
            response = self.client.table("pattern_events").insert(insert_data).execute()
            
            if response.data:
                logger.info(f"Created pattern {pattern_id} for {pattern_data.get('symbol')}")
                return pattern_id
            else:
                logger.error(f"Failed to create pattern: {response}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating pattern: {str(e)}")
            return None
    
    async def update_pattern(self, 
                            pattern_id: str,
                            updates: Dict[str, Any]) -> bool:
        """
        Update an existing pattern
        
        Args:
            pattern_id: Pattern ID
            updates: Fields to update
            
        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            return False
            
        try:
            # Handle JSON fields
            if "draw_commands" in updates and isinstance(updates["draw_commands"], list):
                updates["draw_commands"] = json.dumps(updates["draw_commands"])
            if "metadata" in updates and isinstance(updates["metadata"], dict):
                updates["metadata"] = json.dumps(updates["metadata"])
            if "rule_evaluation" in updates and isinstance(updates["rule_evaluation"], dict):
                updates["rule_evaluation"] = json.dumps(updates["rule_evaluation"])
                
            # Update pattern
            response = self.client.table("pattern_events") \
                .update(updates) \
                .eq("id", pattern_id) \
                .execute()
                
            if response.data:
                logger.info(f"Updated pattern {pattern_id}: {list(updates.keys())}")
                return True
            else:
                logger.error(f"Failed to update pattern {pattern_id}: {response}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating pattern {pattern_id}: {str(e)}")
            return False
    
    async def get_pattern(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a pattern by ID
        
        Args:
            pattern_id: Pattern ID
            
        Returns:
            Pattern data if found, None otherwise
        """
        if not self.client:
            return None
            
        try:
            response = self.client.table("pattern_events") \
                .select("*") \
                .eq("id", pattern_id) \
                .execute()
                
            if response.data and len(response.data) > 0:
                pattern = response.data[0]
                # Parse JSON fields
                if pattern.get("draw_commands"):
                    pattern["draw_commands"] = json.loads(pattern["draw_commands"])
                if pattern.get("metadata"):
                    pattern["metadata"] = json.loads(pattern["metadata"])
                if pattern.get("rule_evaluation"):
                    pattern["rule_evaluation"] = json.loads(pattern["rule_evaluation"])
                return pattern
            return None
            
        except Exception as e:
            logger.error(f"Error getting pattern {pattern_id}: {str(e)}")
            return None
    
    async def get_active_patterns(self, 
                                 symbol: str,
                                 timeframe: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get active patterns for a symbol
        
        Args:
            symbol: Stock symbol
            timeframe: Optional timeframe filter
            
        Returns:
            List of active patterns
        """
        if not self.client:
            return []
            
        try:
            query = self.client.table("pattern_events") \
                .select("*") \
                .eq("symbol", symbol) \
                .in_("status", ["pending", "confirmed"])
                
            if timeframe:
                query = query.eq("timeframe", timeframe)
                
            response = query.order("created_at", desc=True).execute()
            
            if response.data:
                patterns = []
                for pattern in response.data:
                    # Parse JSON fields
                    if pattern.get("draw_commands"):
                        pattern["draw_commands"] = json.loads(pattern["draw_commands"])
                    if pattern.get("metadata"):
                        pattern["metadata"] = json.loads(pattern["metadata"])
                    if pattern.get("rule_evaluation"):
                        pattern["rule_evaluation"] = json.loads(pattern["rule_evaluation"])
                    patterns.append(pattern)
                return patterns
            return []
            
        except Exception as e:
            logger.error(f"Error getting active patterns for {symbol}: {str(e)}")
            return []
    
    async def get_patterns_for_sweep(self, 
                                    max_age_hours: int = 72) -> List[Dict[str, Any]]:
        """
        Get patterns that need lifecycle evaluation
        
        Args:
            max_age_hours: Maximum age before expiration
            
        Returns:
            List of patterns needing evaluation
        """
        if not self.client:
            return []
            
        try:
            # Get active patterns that might need evaluation
            response = self.client.table("pattern_events") \
                .select("*") \
                .in_("status", ["pending", "confirmed"]) \
                .order("created_at", desc=False) \
                .execute()
                
            if response.data:
                patterns = []
                for pattern in response.data:
                    # Parse JSON fields
                    if pattern.get("draw_commands"):
                        pattern["draw_commands"] = json.loads(pattern["draw_commands"])
                    if pattern.get("metadata"):
                        pattern["metadata"] = json.loads(pattern["metadata"])
                    if pattern.get("rule_evaluation"):
                        pattern["rule_evaluation"] = json.loads(pattern["rule_evaluation"])
                    patterns.append(pattern)
                return patterns
            return []
            
        except Exception as e:
            logger.error(f"Error getting patterns for sweep: {str(e)}")
            return []
    
    async def store_verdict(self,
                          pattern_id: str,
                          verdict: str,
                          notes: Optional[str] = None,
                          operator_id: Optional[str] = None) -> bool:
        """
        Store analyst verdict for a pattern
        
        Args:
            pattern_id: Pattern ID
            verdict: Verdict (bullish/bearish/neutral)
            notes: Optional verdict notes
            operator_id: Optional operator ID
            
        Returns:
            True if successful
        """
        updates = {
            "verdict": verdict,
            "verdict_notes": notes,
            "operator_id": operator_id,
            "status": "confirmed" if verdict in ["bullish", "bearish"] else "pending"
        }
        
        # Remove None values
        updates = {k: v for k, v in updates.items() if v is not None}
        
        return await self.update_pattern(pattern_id, updates)
    
    async def get_pattern_statistics(self,
                                    pattern_type: Optional[str] = None,
                                    days: int = 30) -> Dict[str, Any]:
        """
        Get pattern success rate statistics
        
        Args:
            pattern_type: Optional pattern type filter
            days: Number of days to look back
            
        Returns:
            Statistics dictionary
        """
        if not self.client:
            return {}
            
        try:
            # Call stored function for statistics
            params = {"p_days": days}
            if pattern_type:
                params["p_pattern_type"] = pattern_type
                
            response = self.client.rpc("get_pattern_success_stats", params).execute()
            
            if response.data:
                return {
                    "statistics": response.data,
                    "period_days": days,
                    "pattern_type": pattern_type
                }
            return {}
            
        except Exception as e:
            logger.error(f"Error getting pattern statistics: {str(e)}")
            return {}
    
    async def expire_old_patterns(self, max_age_hours: int = 72) -> int:
        """
        Expire patterns older than specified hours
        
        Args:
            max_age_hours: Maximum age in hours
            
        Returns:
            Number of patterns expired
        """
        if not self.client:
            return 0
            
        try:
            response = self.client.rpc(
                "expire_old_patterns",
                {"p_max_age_hours": max_age_hours}
            ).execute()
            
            if response.data:
                count = response.data
                if count > 0:
                    logger.info(f"Expired {count} old patterns")
                return count
            return 0
            
        except Exception as e:
            logger.error(f"Error expiring old patterns: {str(e)}")
            return 0
    
    async def get_lifecycle_history(self,
                                   pattern_id: str,
                                   limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get lifecycle transition history for a pattern
        
        Args:
            pattern_id: Pattern ID
            limit: Maximum number of transitions to return
            
        Returns:
            List of lifecycle transitions
        """
        if not self.client:
            return []
            
        try:
            response = self.client.table("pattern_lifecycle_history") \
                .select("*") \
                .eq("pattern_id", pattern_id) \
                .order("created_at", desc=True) \
                .limit(limit) \
                .execute()
                
            if response.data:
                for record in response.data:
                    if record.get("metadata"):
                        record["metadata"] = json.loads(record["metadata"])
                return response.data
            return []
            
        except Exception as e:
            logger.error(f"Error getting lifecycle history for {pattern_id}: {str(e)}")
            return []
    
    async def bulk_update_patterns(self,
                                  updates: List[Tuple[str, Dict[str, Any]]]) -> int:
        """
        Bulk update multiple patterns
        
        Args:
            updates: List of (pattern_id, updates_dict) tuples
            
        Returns:
            Number of successfully updated patterns
        """
        success_count = 0
        for pattern_id, update_data in updates:
            if await self.update_pattern(pattern_id, update_data):
                success_count += 1
        return success_count