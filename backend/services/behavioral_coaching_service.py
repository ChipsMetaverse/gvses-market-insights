"""
Behavioral Coaching Service - Phase 1
Progressive Behavioral Architecture for Trading Psychology

This service implements non-directive mental skill development based on:
- ACT (Acceptance and Commitment Therapy) principles
- Behavioral analytics and pattern detection
- Just-in-Time learning vs Just-in-Case courses

Regulatory Positioning:
- Educational wellness tool (NOT investment advice)
- General stress management (NOT medical treatment)
- User-controlled insights (NOT automated trading)
"""

import logging
from datetime import datetime, timedelta, timezone as tz
from typing import List, Dict, Optional, Any
from supabase import Client
import json

logger = logging.getLogger(__name__)


class BehavioralCoachingService:
    """
    Core service for behavioral coaching features.

    Implements the "Reflection Engine" from Phase 1:
    - Trade journaling with emotional context
    - Weekly behavioral insights
    - ACT exercise delivery
    - Pattern detection and educational feedback
    """

    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        logger.info("✅ Behavioral Coaching Service initialized")

    # =========================================================================
    # TRADE JOURNAL METHODS
    # =========================================================================

    async def capture_trade(
        self,
        user_id: str,
        symbol: str,
        entry_price: float,
        exit_price: Optional[float],
        entry_timestamp: datetime,
        exit_timestamp: Optional[datetime],
        position_size: int,
        direction: str,
        timeframe: str,
        emotional_tags: List[str] = None,
        plan_entry: str = None,
        plan_exit: str = None,
        actual_vs_plan: str = None,
        stress_level: int = None,
        confidence_level: int = None,
        chart_snapshot_url: str = None,
        market_conditions: Dict = None,
        voice_plan_url: str = None,
        voice_review_url: str = None
    ) -> Dict[str, Any]:
        """
        Capture a trade in the journal with psychological context.

        This is the foundation of the Reflection Engine - allowing traders
        to document not just WHAT they traded, but WHY and HOW they felt.

        Args:
            user_id: User's UUID
            symbol: Stock ticker (e.g., TSLA)
            entry_price: Entry price
            exit_price: Exit price (None if still open)
            entry_timestamp: When trade was entered
            exit_timestamp: When trade was exited (None if open)
            position_size: Number of shares
            direction: 'long' or 'short'
            timeframe: Chart timeframe used
            emotional_tags: Array of emotional states (optional)
            plan_entry: Written trade plan (optional)
            plan_exit: Planned exit strategy (optional)
            actual_vs_plan: Reflection on plan adherence (optional)
            stress_level: 1-10 self-reported stress (optional)
            confidence_level: 1-10 self-reported confidence (optional)
            chart_snapshot_url: Screenshot URL from storage (optional)
            market_conditions: Technical levels, BTD, etc (optional)
            voice_plan_url: Pre-trade voice memo URL (optional)
            voice_review_url: Post-trade reflection voice memo (optional)

        Returns:
            Dict with trade_id and behavioral flags
        """
        try:
            # Calculate P/L if exit data provided
            pl = None
            pl_percent = None
            if exit_price is not None:
                if direction == 'long':
                    pl = (exit_price - entry_price) * position_size
                    pl_percent = ((exit_price - entry_price) / entry_price) * 100
                else:  # short
                    pl = (entry_price - exit_price) * position_size
                    pl_percent = ((entry_price - exit_price) / entry_price) * 100

            # Build trade data
            trade_data = {
                'user_id': user_id,
                'symbol': symbol.upper(),
                'entry_price': entry_price,
                'exit_price': exit_price,
                'entry_timestamp': entry_timestamp.isoformat(),
                'exit_timestamp': exit_timestamp.isoformat() if exit_timestamp else None,
                'position_size': position_size,
                'direction': direction,
                'pl': round(pl, 2) if pl is not None else None,
                'pl_percent': round(pl_percent, 4) if pl_percent is not None else None,
                'timeframe': timeframe,
                'emotional_tags': emotional_tags or [],
                'plan_entry': plan_entry,
                'plan_exit': plan_exit,
                'actual_vs_plan': actual_vs_plan,
                'stress_level': stress_level,
                'confidence_level': confidence_level,
                'chart_snapshot_url': chart_snapshot_url,
                'market_conditions': market_conditions or {},
                'voice_plan_url': voice_plan_url,
                'voice_review_url': voice_review_url
            }

            # Insert into Supabase
            # Behavioral flags (is_disciplined, is_revenge, etc) computed by DB trigger
            result = self.supabase.table('trade_journal').insert(trade_data).execute()

            if result.data and len(result.data) > 0:
                trade = result.data[0]
                pl_str = f"${pl:.2f}" if pl is not None else "open"
                logger.info(
                    f"📝 Trade captured: {symbol} {direction} @ ${entry_price} "
                    f"(P/L: {pl_str})"
                )

                # Check if this trade triggers ACT exercises
                await self._check_act_triggers(user_id, trade['id'], trade)

                return {
                    'success': True,
                    'trade_id': trade['id'],
                    'behavioral_flags': {
                        'is_disciplined': trade.get('is_disciplined'),
                        'is_impulsive': trade.get('is_impulsive'),
                        'is_fomo': trade.get('is_fomo'),
                        'is_revenge': trade.get('is_revenge')
                    },
                    'pl': pl,
                    'pl_percent': pl_percent
                }
            else:
                logger.error("❌ Trade journal insert returned no data")
                return {'success': False, 'error': 'Insert failed'}

        except Exception as e:
            logger.error(f"❌ Trade capture error: {e}")
            return {'success': False, 'error': str(e)}

    async def get_journal_entries(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
        symbol: str = None,
        start_date: datetime = None,
        end_date: datetime = None,
        emotional_filter: List[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve journal entries with filters.

        Args:
            user_id: User's UUID
            limit: Number of entries to return
            offset: Pagination offset
            symbol: Filter by specific symbol (optional)
            start_date: Filter trades after this date (optional)
            end_date: Filter trades before this date (optional)
            emotional_filter: Filter by emotional tags (optional)

        Returns:
            Dict with entries array and total count
        """
        try:
            # Build query
            query = self.supabase.table('trade_journal') \
                .select('*', count='exact') \
                .eq('user_id', user_id) \
                .order('entry_timestamp', desc=True) \
                .limit(limit) \
                .offset(offset)

            # Apply filters
            if symbol:
                query = query.eq('symbol', symbol.upper())

            if start_date:
                query = query.gte('entry_timestamp', start_date.isoformat())

            if end_date:
                query = query.lte('entry_timestamp', end_date.isoformat())

            if emotional_filter:
                query = query.contains('emotional_tags', emotional_filter)

            # Execute query
            result = query.execute()

            return {
                'success': True,
                'entries': result.data,
                'total_count': result.count
            }

        except Exception as e:
            logger.error(f"❌ Journal retrieval error: {e}")
            return {'success': False, 'error': str(e)}

    # =========================================================================
    # WEEKLY INSIGHTS METHODS
    # =========================================================================

    async def get_weekly_insights(
        self,
        user_id: str,
        week_start: datetime = None
    ) -> Dict[str, Any]:
        """
        Get behavioral insights for a specific week.

        If week_start not provided, returns current week.
        Insights show the "cost" of emotional trading in concrete terms.

        Args:
            user_id: User's UUID
            week_start: Start of target week (defaults to current week)

        Returns:
            Dict with behavioral metrics and emotional costs
        """
        try:
            # Default to current week if not specified
            if week_start is None:
                today = datetime.now(tz.utc)
                week_start = today - timedelta(days=today.weekday())  # Monday
                week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)

            week_start_date = week_start.date()

            # Check if insights already computed
            result = self.supabase.table('weekly_insights') \
                .select('*') \
                .eq('user_id', user_id) \
                .eq('week_start', week_start_date.isoformat()) \
                .execute()

            if result.data and len(result.data) > 0:
                # Return cached insights
                logger.info(f"📊 Retrieved cached insights for week of {week_start_date}")
                return {
                    'success': True,
                    'insights': result.data[0],
                    'cached': True
                }
            else:
                # Compute fresh insights
                logger.info(f"🔄 Computing fresh insights for week of {week_start_date}")

                # Call stored procedure to compute insights
                self.supabase.rpc(
                    'update_weekly_insights',
                    {
                        'target_user_id': user_id,
                        'target_week_start': week_start_date.isoformat()
                    }
                ).execute()

                # Retrieve freshly computed insights
                result = self.supabase.table('weekly_insights') \
                    .select('*') \
                    .eq('user_id', user_id) \
                    .eq('week_start', week_start_date.isoformat()) \
                    .execute()

                if result.data and len(result.data) > 0:
                    return {
                        'success': True,
                        'insights': result.data[0],
                        'cached': False
                    }
                else:
                    return {
                        'success': True,
                        'insights': None,
                        'message': 'No trades this week yet'
                    }

        except Exception as e:
            logger.error(f"❌ Weekly insights error: {e}")
            return {'success': False, 'error': str(e)}

    # =========================================================================
    # ACT EXERCISE METHODS
    # =========================================================================

    async def get_act_exercises(
        self,
        exercise_type: str = None,
        trigger_context: str = None
    ) -> Dict[str, Any]:
        """
        Get ACT exercises from library.

        Args:
            exercise_type: Filter by type (optional)
            trigger_context: Filter by trigger context (optional)

        Returns:
            Dict with exercises array
        """
        try:
            query = self.supabase.table('act_exercises') \
                .select('*') \
                .eq('is_active', True) \
                .order('difficulty')

            if exercise_type:
                query = query.eq('type', exercise_type)

            if trigger_context:
                query = query.contains('trigger_contexts', [trigger_context])

            result = query.execute()

            return {
                'success': True,
                'exercises': result.data
            }

        except Exception as e:
            logger.error(f"❌ ACT exercises retrieval error: {e}")
            return {'success': False, 'error': str(e)}

    async def record_act_completion(
        self,
        user_id: str,
        exercise_id: str,
        trigger_context: str,
        related_trade_id: str = None,
        completed: bool = True,
        duration_seconds: int = None,
        quality_rating: int = None,
        user_notes: str = None,
        prevented_impulsive_trade: bool = None,
        improved_emotional_state: bool = None
    ) -> Dict[str, Any]:
        """
        Record completion of an ACT exercise.

        Args:
            user_id: User's UUID
            exercise_id: UUID of exercise from library
            trigger_context: What triggered this exercise
            related_trade_id: Trade that triggered it (optional)
            completed: Whether user finished it
            duration_seconds: How long they spent
            quality_rating: 1-5 self-reported quality
            user_notes: Reflection notes
            prevented_impulsive_trade: Did it stop impulsive action?
            improved_emotional_state: Did it help emotionally?

        Returns:
            Dict with completion_id
        """
        try:
            completion_data = {
                'user_id': user_id,
                'exercise_id': exercise_id,
                'trigger_context': trigger_context,
                'related_trade_id': related_trade_id,
                'completed': completed,
                'duration_seconds': duration_seconds,
                'quality_rating': quality_rating,
                'user_notes': user_notes,
                'prevented_impulsive_trade': prevented_impulsive_trade,
                'improved_emotional_state': improved_emotional_state,
                'completed_at': datetime.now(tz.utc).isoformat() if completed else None
            }

            result = self.supabase.table('act_exercise_completions') \
                .insert(completion_data) \
                .execute()

            if result.data and len(result.data) > 0:
                logger.info(
                    f"🧠 ACT exercise completed: {trigger_context} "
                    f"(prevented impulsive: {prevented_impulsive_trade})"
                )
                return {
                    'success': True,
                    'completion_id': result.data[0]['id']
                }
            else:
                return {'success': False, 'error': 'Insert failed'}

        except Exception as e:
            logger.error(f"❌ ACT completion recording error: {e}")
            return {'success': False, 'error': str(e)}

    async def _check_act_triggers(
        self,
        user_id: str,
        trade_id: str,
        trade_data: Dict
    ) -> None:
        """
        Internal method to check if a trade should trigger ACT exercises.

        Implements "Just-in-Time" learning - exercises delivered at the
        moment of need, not randomly or via courses.

        Args:
            user_id: User's UUID
            trade_id: Trade that might trigger exercise
            trade_data: Trade details for pattern matching
        """
        try:
            # Check user settings - are ACT exercises enabled?
            settings_result = self.supabase.table('user_behavioral_settings') \
                .select('*') \
                .eq('user_id', user_id) \
                .execute()

            if not settings_result.data or not settings_result.data[0].get('act_exercises_enabled', True):
                return  # User has disabled ACT exercises

            trigger_contexts = []

            # Detect trigger conditions based on behavioral flags
            if trade_data.get('is_revenge'):
                trigger_contexts.append('revenge_trading_risk')

            if trade_data.get('is_fomo'):
                trigger_contexts.append('pre_fomo_entry')

            if trade_data.get('pl', 0) < 0:  # Loss
                trigger_contexts.append('post_stopout')

            # Check for loss streaks
            recent_trades = self.supabase.table('trade_journal') \
                .select('pl') \
                .eq('user_id', user_id) \
                .order('entry_timestamp', desc=True) \
                .limit(5) \
                .execute()

            if recent_trades.data:
                losses = [t for t in recent_trades.data if t.get('pl', 0) < 0]
                if len(losses) >= 3:
                    trigger_contexts.append('after_loss_streak')

            # Recommend exercises based on triggers
            for context in trigger_contexts:
                exercises_result = await self.get_act_exercises(trigger_context=context)

                if exercises_result['success'] and exercises_result['exercises']:
                    # Log that exercise was triggered (user can choose to do it)
                    logger.info(
                        f"🎯 ACT exercise triggered: {context} for trade {trade_id}"
                    )
                    # Frontend will display exercise prompt
                    # Actual completion tracked when user engages

        except Exception as e:
            logger.error(f"❌ ACT trigger check error: {e}")

    # =========================================================================
    # BEHAVIORAL PATTERN DETECTION
    # =========================================================================

    async def detect_behavioral_patterns(
        self,
        user_id: str,
        min_trades: int = 20
    ) -> Dict[str, Any]:
        """
        Analyze trading history to detect behavioral patterns.

        This implements educational insights (NOT investment advice).
        Patterns are presented as data-driven observations, allowing
        traders to see their own behavioral leaks.

        Requires minimum number of trades for statistical validity
        (avoids false positives with small samples).

        Args:
            user_id: User's UUID
            min_trades: Minimum trades required for pattern detection

        Returns:
            Dict with detected patterns array
        """
        try:
            # Get all closed trades for analysis
            trades_result = self.supabase.table('trade_journal') \
                .select('*') \
                .eq('user_id', user_id) \
                .not_.is_('exit_timestamp', 'null') \
                .order('entry_timestamp', desc=False) \
                .execute()

            trades = trades_result.data if trades_result.data else []

            if len(trades) < min_trades:
                return {
                    'success': True,
                    'patterns': [],
                    'message': f'Need {min_trades} trades for pattern detection (have {len(trades)})'
                }

            detected_patterns = []

            # Pattern 1: Revenge Trading
            revenge_pattern = self._detect_revenge_trading(trades)
            if revenge_pattern:
                detected_patterns.append(revenge_pattern)

            # Pattern 2: FOMO Entries
            fomo_pattern = self._detect_fomo_trading(trades)
            if fomo_pattern:
                detected_patterns.append(fomo_pattern)

            # Pattern 3: Time-of-Day Bias
            time_pattern = self._detect_time_bias(trades)
            if time_pattern:
                detected_patterns.append(time_pattern)

            # Store detected patterns in database
            for pattern in detected_patterns:
                # Check if this pattern already exists
                existing = self.supabase.table('behavioral_patterns') \
                    .select('*') \
                    .eq('user_id', user_id) \
                    .eq('pattern_type', pattern['pattern_type']) \
                    .eq('acknowledged', False) \
                    .execute()

                if not existing.data:  # Only insert if new
                    pattern['user_id'] = user_id
                    self.supabase.table('behavioral_patterns').insert(pattern).execute()

            logger.info(f"🔍 Detected {len(detected_patterns)} behavioral patterns")

            return {
                'success': True,
                'patterns': detected_patterns,
                'total_trades_analyzed': len(trades)
            }

        except Exception as e:
            logger.error(f"❌ Pattern detection error: {e}")
            return {'success': False, 'error': str(e)}

    def _detect_revenge_trading(self, trades: List[Dict]) -> Optional[Dict]:
        """Detect revenge trading pattern."""
        revenge_trades = [t for t in trades if t.get('is_revenge')]

        if len(revenge_trades) < 3:
            return None

        revenge_wins = len([t for t in revenge_trades if t.get('pl', 0) > 0])
        revenge_win_rate = revenge_wins / len(revenge_trades)
        avg_revenge_loss = sum([t['pl'] for t in revenge_trades if t['pl'] < 0]) / max(1, len([t for t in revenge_trades if t['pl'] < 0]))

        if revenge_win_rate < 0.35:  # <35% win rate = problematic pattern
            return {
                'pattern_type': 'revenge_trading',
                'confidence': 0.85,
                'severity': 'high' if revenge_win_rate < 0.25 else 'medium',
                'supporting_trades': [t['id'] for t in revenge_trades],
                'sample_size': len(revenge_trades),
                'title': 'Revenge Trading Pattern Detected',
                'description': f'You lose money {len(revenge_trades) - revenge_wins}/{len(revenge_trades)} times when trading within 10 minutes of a stop-out',
                'suggestion': 'Consider implementing a 10-minute cooling-off period after losses to allow emotional regulation',
                'pattern_metrics': {
                    'win_rate': round(revenge_win_rate, 2),
                    'avg_loss': round(avg_revenge_loss, 2),
                    'frequency': len(revenge_trades)
                }
            }

        return None

    def _detect_fomo_trading(self, trades: List[Dict]) -> Optional[Dict]:
        """Detect FOMO (Fear of Missing Out) trading pattern."""
        fomo_trades = [t for t in trades if t.get('is_fomo')]

        if len(fomo_trades) < 3:
            return None

        fomo_wins = len([t for t in fomo_trades if t.get('pl', 0) > 0])
        fomo_win_rate = fomo_wins / len(fomo_trades)
        avg_fomo_pl = sum([t['pl'] for t in fomo_trades]) / len(fomo_trades)

        if avg_fomo_pl < 0:  # Net negative from FOMO trades
            return {
                'pattern_type': 'fomo_entries',
                'confidence': 0.80,
                'severity': 'high' if avg_fomo_pl < -100 else 'medium',
                'supporting_trades': [t['id'] for t in fomo_trades],
                'sample_size': len(fomo_trades),
                'title': 'FOMO Entry Pattern Detected',
                'description': f'Your FOMO trades (after rapid price movements) have a {round(fomo_win_rate * 100, 1)}% win rate and average ${round(avg_fomo_pl, 2)} P/L',
                'suggestion': 'Practice the "Leaves on Stream" ACT exercise to observe FOMO thoughts without acting on them',
                'pattern_metrics': {
                    'win_rate': round(fomo_win_rate, 2),
                    'avg_pl': round(avg_fomo_pl, 2),
                    'frequency': len(fomo_trades)
                }
            }

        return None

    def _detect_time_bias(self, trades: List[Dict]) -> Optional[Dict]:
        """Detect time-of-day performance bias."""
        # Group trades by hour of day
        from collections import defaultdict
        hourly_performance = defaultdict(list)

        for trade in trades:
            entry_time = datetime.fromisoformat(trade['entry_timestamp'].replace('Z', '+00:00'))
            hour = entry_time.hour
            hourly_performance[hour].append(trade['pl'])

        # Find best and worst hours (need 5+ trades per hour)
        best_hour = None
        best_avg_pl = -999999
        worst_hour = None
        worst_avg_pl = 999999

        for hour, pls in hourly_performance.items():
            if len(pls) >= 5:
                avg_pl = sum(pls) / len(pls)
                if avg_pl > best_avg_pl:
                    best_avg_pl = avg_pl
                    best_hour = hour
                if avg_pl < worst_avg_pl:
                    worst_avg_pl = avg_pl
                    worst_hour = hour

        if best_hour is not None and worst_hour is not None and abs(best_avg_pl - worst_avg_pl) > 50:
            return {
                'pattern_type': 'time_of_day_bias',
                'confidence': 0.75,
                'severity': 'medium',
                'supporting_trades': [],
                'sample_size': len(trades),
                'title': 'Time-of-Day Performance Pattern',
                'description': f'Your best trading hour is {best_hour}:00 (avg ${round(best_avg_pl, 2)}), worst is {worst_hour}:00 (avg ${round(worst_avg_pl, 2)})',
                'suggestion': f'Consider focusing trading activity around {best_hour}:00 and avoiding {worst_hour}:00',
                'pattern_metrics': {
                    'best_hour': best_hour,
                    'best_avg_pl': round(best_avg_pl, 2),
                    'worst_hour': worst_hour,
                    'worst_avg_pl': round(worst_avg_pl, 2)
                }
            }

        return None


# =========================================================================
# SINGLETON INSTANCE
# =========================================================================

_behavioral_coaching_service = None

def get_behavioral_coaching_service(supabase_client: Client = None) -> BehavioralCoachingService:
    """Get or create singleton instance."""
    global _behavioral_coaching_service

    if _behavioral_coaching_service is None:
        if supabase_client is None:
            raise ValueError("Must provide supabase_client for first initialization")
        _behavioral_coaching_service = BehavioralCoachingService(supabase_client)

    return _behavioral_coaching_service
